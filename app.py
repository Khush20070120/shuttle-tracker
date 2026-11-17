import os
import sqlite3

from flask import Flask, request, render_template, redirect, session, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from model import predict_delay_minutes

app = Flask(__name__)
app.secret_key = "secret123"
DB_PATH = os.path.join(os.path.dirname(__file__), "shuttle_tracker.db")


def _sqlite_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_db():
    try:
        conn = mysql.connector.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            user=os.environ.get("DB_USER", "root"),
            password=os.environ.get("DB_PASSWORD", ""),
            database=os.environ.get("DB_NAME", "shuttle_tracker1"),
            port=int(os.environ.get("DB_PORT", "3306")),
        )
        app.config["DB_ENGINE"] = "mysql"
        return conn
    except mysql.connector.Error:
        conn = _sqlite_db()
        app.config["DB_ENGINE"] = "sqlite"
        return conn


def db_placeholder():
    return "?" if app.config.get("DB_ENGINE") == "sqlite" else "%s"


def db_placeholders(count):
    return ", ".join(db_placeholder() for _ in range(count))


def row_to_dict(row):
    if row is None:
        return None
    if isinstance(row, dict):
        return row
    return {key: row[key] for key in row.keys()}


def ensure_db():
    conn = _sqlite_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT DEFAULT 'user'
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS LoginLogs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            role TEXT,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS Bus (
            bus_id INTEGER PRIMARY KEY AUTOINCREMENT,
            bus_number TEXT,
            capacity INTEGER,
            departure_time TEXT,
            arrival_time TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS Route (
            route_id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            destination TEXT,
            departure_time TEXT,
            arrival_time TEXT
        )
        """
    )

    if conn.execute("SELECT COUNT(*) FROM Users").fetchone()[0] == 0:
        conn.execute(
            "INSERT INTO Users (username, password, role) VALUES (?, ?, ?)",
            ("admin", generate_password_hash("admin123", method="pbkdf2:sha256"), "admin"),
        )
        conn.execute(
            "INSERT INTO Users (username, password, role) VALUES (?, ?, ?)",
            ("user1", generate_password_hash("user123", method="pbkdf2:sha256"), "user"),
        )

    if conn.execute("SELECT COUNT(*) FROM Bus").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO Bus (bus_number, capacity, departure_time, arrival_time) VALUES (?, ?, ?, ?)",
            [
                ("BUS-101", 42, "08:00:00", "09:00:00"),
                ("BUS-202", 36, "09:30:00", "10:45:00"),
            ],
        )

    if conn.execute("SELECT COUNT(*) FROM Route").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO Route (source, destination, departure_time, arrival_time) VALUES (?, ?, ?, ?)",
            [
                ("Campus", "City Center", "08:10:00", "09:10:00"),
                ("Station", "College", "12:00:00", "13:00:00"),
            ],
        )

    conn.commit()
    conn.close()


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
                f"INSERT INTO Users (username, password, role) VALUES ({db_placeholders(3)})",
                (username, hashed_password, role),
            )
            conn.commit()
            conn.close()
            return redirect("/")
        except mysql.connector.Error:
            return "User already exists or database error"

    return render_template("signup.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"].strip()
    password = request.form["password"]

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM Users WHERE username={db_placeholder()}", (username,))
    user = cursor.fetchone()
    if user is not None and app.config.get("DB_ENGINE") == "sqlite":
        user = row_to_dict(user)

    if user and check_password_hash(user["password"], password):
        session["username"] = user["username"]
        session["role"] = user["role"]

        log_cursor = conn.cursor()
        log_cursor.execute(
            f"INSERT INTO LoginLogs (username, role) VALUES ({db_placeholders(2)})",
            (user["username"], user["role"]),
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
        f"INSERT INTO Bus (bus_number, capacity, departure_time, arrival_time) VALUES ({db_placeholders(4)})",
        (data["bus_number"], data["capacity"], data["departure_time"], data["arrival_time"]),
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
        f"INSERT INTO Route (source, destination, departure_time, arrival_time) VALUES ({db_placeholders(4)})",
        (data["source"], data["destination"], data["departure_time"], data["arrival_time"]),
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
        f"UPDATE Bus SET bus_number={db_placeholder()}, capacity={db_placeholder()}, departure_time={db_placeholder()}, arrival_time={db_placeholder()} WHERE bus_id={db_placeholder()}",
        (data["bus_number"], data["capacity"], data["departure_time"], data["arrival_time"], bus_id),
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
        f"UPDATE Route SET source={db_placeholder()}, destination={db_placeholder()}, departure_time={db_placeholder()}, arrival_time={db_placeholder()} WHERE route_id={db_placeholder()}",
        (data["source"], data["destination"], data["departure_time"], data["arrival_time"], route_id),
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
    cursor.execute(f"DELETE FROM Bus WHERE bus_id={db_placeholder()}", (bus_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})


@app.route("/delete_route/<int:route_id>", methods=["DELETE"])
def delete_route(route_id):
    if not admin_required():
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM Route WHERE route_id={db_placeholder()}", (route_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "deleted"})


@app.route("/combined_data")
def combined_data():
    if not login_required():
        return jsonify([])

    conn = get_db()

    if app.config.get("DB_ENGINE") == "sqlite":
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                'Bus' AS item_type,
                bus_id AS item_id,
                bus_number AS value_1,
                CAST(capacity AS TEXT) AS value_2,
                departure_time,
                arrival_time
            FROM Bus
            ORDER BY bus_id DESC
            """
        )
        bus_rows = [row_to_dict(r) for r in cursor.fetchall()]

        cursor.execute(
            """
            SELECT
                'Route' AS item_type,
                route_id AS item_id,
                source AS value_1,
                destination AS value_2,
                departure_time,
                arrival_time
            FROM Route
            ORDER BY route_id DESC
            """
        )
        route_rows = [row_to_dict(r) for r in cursor.fetchall()]
    else:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                'Bus' AS item_type,
                bus_id AS item_id,
                bus_number AS value_1,
                CAST(capacity AS CHAR) AS value_2,
                departure_time,
                arrival_time
            FROM Bus
            ORDER BY bus_id DESC
            """
        )
        bus_rows = cursor.fetchall()

        cursor.execute(
            """
            SELECT
                'Route' AS item_type,
                route_id AS item_id,
                source AS value_1,
                destination AS value_2,
                departure_time,
                arrival_time
            FROM Route
            ORDER BY route_id DESC
            """
        )
        route_rows = cursor.fetchall()

    conn.close()

    combined = []
    for row in bus_rows + route_rows:
        combined.append(
            {
                "item_type": row["item_type"],
                "item_id": row["item_id"],
                "value_1": row["value_1"],
                "value_2": row["value_2"],
                "departure_time": time_to_str(row["departure_time"]),
                "arrival_time": time_to_str(row["arrival_time"]),
            }
        )

    combined.sort(key=lambda x: (x["item_type"], -int(x["item_id"])))
    return jsonify(combined)


@app.route("/analytics")
def analytics():
    if not admin_required():
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db()

    if app.config.get("DB_ENGINE") == "sqlite":
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total_buses FROM Bus")
        total_buses = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) AS total_routes FROM Route")
        total_routes = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) AS total_logins FROM LoginLogs")
        total_logins = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(AVG(capacity), 0) AS avg_capacity FROM Bus")
        avg_capacity = float(cursor.fetchone()[0])

        cursor.execute(
            """
            SELECT username, COUNT(*) AS login_count
            FROM LoginLogs
            GROUP BY username
            ORDER BY login_count DESC
            LIMIT 5
            """
        )
        top_users = [row_to_dict(row) for row in cursor.fetchall()]

        cursor.execute(
            """
            SELECT CAST(strftime('%H', login_time) AS INTEGER) AS login_hour, COUNT(*) AS count
            FROM LoginLogs
            GROUP BY strftime('%H', login_time)
            ORDER BY login_hour
            """
        )
        login_by_hour = [row_to_dict(row) for row in cursor.fetchall()]
    else:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) AS total_buses FROM Bus")
        total_buses = cursor.fetchone()["total_buses"]

        cursor.execute("SELECT COUNT(*) AS total_routes FROM Route")
        total_routes = cursor.fetchone()["total_routes"]

        cursor.execute("SELECT COUNT(*) AS total_logins FROM LoginLogs")
        total_logins = cursor.fetchone()["total_logins"]

        cursor.execute("SELECT IFNULL(AVG(capacity),0) AS avg_capacity FROM Bus")
        avg_capacity = float(cursor.fetchone()["avg_capacity"])

        cursor.execute(
            """
            SELECT username, COUNT(*) AS login_count
            FROM LoginLogs
            GROUP BY username
            ORDER BY login_count DESC
            LIMIT 5
            """
        )
        top_users = cursor.fetchall()

        cursor.execute(
            """
            SELECT HOUR(login_time) AS login_hour, COUNT(*) AS count
            FROM LoginLogs
            GROUP BY HOUR(login_time)
            ORDER BY login_hour
            """
        )
        login_by_hour = cursor.fetchall()

    conn.close()

    return jsonify(
        {
            "total_buses": total_buses,
            "total_routes": total_routes,
            "total_logins": total_logins,
            "avg_capacity": round(avg_capacity, 2),
            "top_users": top_users,
            "login_by_hour": login_by_hour,
        }
    )


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
    ensure_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5001")), debug=True)
