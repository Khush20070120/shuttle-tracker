from flask import Flask, request, render_template, redirect, session, jsonify
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from model import predict_delay_minutes

app = Flask(__name__)
app.secret_key = "secret123"


def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",   # put your MySQL password here if needed
        database="shuttle_tracker1"
    )


def login_required():
    return "username" in session


def admin_required():
    return session.get("role") == "admin"


def time_to_str(value):
    if value is None:
        return None
    return str(value)[:5]


@app.route("/")
def home():
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        role = request.form["role"]

        if not username or not password:
            return "Username and password required"

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Users (username, password, role) VALUES (%s, %s, %s)",
                (username, hashed_password, role)
            )
            conn.commit()
            conn.close()
            return redirect("/")
        except Error:
            return "User already exists or database error"

    return render_template("signup.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"].strip()
    password = request.form["password"]

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Users WHERE username=%s", (username,))
    user = cursor.fetchone()

    if user and check_password_hash(user["password"], password):
        session["username"] = user["username"]
        session["role"] = user["role"]

        log_cursor = conn.cursor()
        log_cursor.execute(
            "INSERT INTO LoginLogs (username, role) VALUES (%s, %s)",
            (user["username"], user["role"])
        )
        conn.commit()
        conn.close()

        return redirect("/admin" if user["role"] == "admin" else "/user")

    conn.close()
    return "Invalid login"


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/admin")
def admin():
    if not admin_required():
        return "Unauthorized"
    return render_template("admin.html", username=session.get("username", "Admin"))


@app.route("/user")
def user():
    if not login_required():
        return redirect("/")
    return render_template("user.html", username=session.get("username", "User"))


@app.route("/add_bus", methods=["POST"])
def add_bus():
    if not admin_required():
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO Bus (bus_number, capacity, departure_time, arrival_time)
        VALUES (%s, %s, %s, %s)
        """,
        (
            data["bus_number"],
            data["capacity"],
            data["departure_time"],
            data["arrival_time"]
        )
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})


@app.route("/add_route", methods=["POST"])
def add_route():
    if not admin_required():
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO Route (source, destination, departure_time, arrival_time)
        VALUES (%s, %s, %s, %s)
        """,
        (
            data["source"],
            data["destination"],
            data["departure_time"],
            data["arrival_time"]
        )
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})


@app.route("/update_bus/<int:bus_id>", methods=["PUT"])
def update_bus(bus_id):
    if not admin_required():
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE Bus
        SET bus_number=%s, capacity=%s, departure_time=%s, arrival_time=%s
        WHERE bus_id=%s
        """,
        (
            data["bus_number"],
            data["capacity"],
            data["departure_time"],
            data["arrival_time"],
            bus_id
        )
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "updated"})


@app.route("/update_route/<int:route_id>", methods=["PUT"])
def update_route(route_id):
    if not admin_required():
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE Route
        SET source=%s, destination=%s, departure_time=%s, arrival_time=%s
        WHERE route_id=%s
        """,
        (
            data["source"],
            data["destination"],
            data["departure_time"],
            data["arrival_time"],
            route_id
        )
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "updated"})


@app.route("/delete_bus/<int:bus_id>", methods=["DELETE"])
def delete_bus(bus_id):
    if not admin_required():
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Bus WHERE bus_id=%s", (bus_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})


@app.route("/delete_route/<int:route_id>", methods=["DELETE"])
def delete_route(route_id):
    if not admin_required():
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Route WHERE route_id=%s", (route_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})


@app.route("/combined_data")
def combined_data():
    if not login_required():
        return jsonify([])

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            'Bus' AS item_type,
            bus_id AS item_id,
            bus_number AS value_1,
            CAST(capacity AS CHAR) AS value_2,
            departure_time,
            arrival_time
        FROM Bus
        ORDER BY bus_id DESC
    """)
    bus_rows = cursor.fetchall()

    cursor.execute("""
        SELECT
            'Route' AS item_type,
            route_id AS item_id,
            source AS value_1,
            destination AS value_2,
            departure_time,
            arrival_time
        FROM Route
        ORDER BY route_id DESC
    """)
    route_rows = cursor.fetchall()

    conn.close()

    combined = []

    for row in bus_rows + route_rows:
        combined.append({
            "item_type": row["item_type"],
            "item_id": row["item_id"],
            "value_1": row["value_1"],
            "value_2": row["value_2"],
            "departure_time": time_to_str(row["departure_time"]),
            "arrival_time": time_to_str(row["arrival_time"])
        })

    combined.sort(key=lambda x: (x["item_type"], -int(x["item_id"])))
    return jsonify(combined)


@app.route("/analytics")
def analytics():
    if not admin_required():
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total_buses FROM Bus")
    total_buses = cursor.fetchone()["total_buses"]

    cursor.execute("SELECT COUNT(*) AS total_routes FROM Route")
    total_routes = cursor.fetchone()["total_routes"]

    cursor.execute("SELECT COUNT(*) AS total_logins FROM LoginLogs")
    total_logins = cursor.fetchone()["total_logins"]

    cursor.execute("SELECT IFNULL(AVG(capacity),0) AS avg_capacity FROM Bus")
    avg_capacity = float(cursor.fetchone()["avg_capacity"])

    cursor.execute("""
        SELECT username, COUNT(*) AS login_count
        FROM LoginLogs
        GROUP BY username
        ORDER BY login_count DESC
        LIMIT 5
    """)
    top_users = cursor.fetchall()

    cursor.execute("""
        SELECT HOUR(login_time) AS login_hour, COUNT(*) AS count
        FROM LoginLogs
        GROUP BY HOUR(login_time)
        ORDER BY login_hour
    """)
    login_by_hour = cursor.fetchall()

    conn.close()

    return jsonify({
        "total_buses": total_buses,
        "total_routes": total_routes,
        "total_logins": total_logins,
        "avg_capacity": round(avg_capacity, 2),
        "top_users": top_users,
        "login_by_hour": login_by_hour
    })


@app.route("/predict_delay", methods=["POST"])
def predict_delay():
    if not login_required():
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    traffic = float(data["traffic"])
    distance = float(data["distance"])
    weather = float(data["weather"])

    prediction = predict_delay_minutes(traffic, distance, weather)
    return jsonify({"predicted_delay_minutes": prediction})


if __name__ == "__main__":
    app.run(debug=True)