let combinedData = [];
let loginChartInstance = null;
let userChartInstance = null;

async function getJSON(url) {
    const res = await fetch(url);
    return await res.json();
}

function isAdminPage() {
    return window.location.pathname === "/admin";
}

function formatTime(value) {
    if (!value) return "-";
    return String(value).slice(0, 5);
}

async function loadCombinedData() {
    combinedData = await getJSON("/combined_data");
    renderCombinedTable();
}

function renderCombinedTable() {
    const tbody = document.getElementById("combinedTableBody");
    if (!tbody) return;

    const searchValue = (document.getElementById("searchInput")?.value || "").toLowerCase();
    const typeValue = document.getElementById("typeFilter")?.value || "All";

    tbody.innerHTML = "";

    const filtered = combinedData.filter(item => {
        const matchesType = typeValue === "All" || item.item_type === typeValue;
        const text = `${item.item_type} ${item.item_id} ${item.col1} ${item.col2} ${item.departure_time} ${item.arrival_time}`.toLowerCase();
        const matchesSearch = text.includes(searchValue);
        return matchesType && matchesSearch;
    });

    filtered.forEach(item => {
        const row = document.createElement("tr");

        let actions = "";
        if (isAdminPage()) {
            if (item.item_type === "Bus") {
                actions = `
                    <button class="action-btn edit-btn" onclick='editBus(${JSON.stringify(item)})'>Edit</button>
                    <button class="action-btn delete-btn" onclick='deleteBus(${item.item_id})'>Delete</button>
                `;
            } else {
                actions = `
                    <button class="action-btn edit-btn" onclick='editRoute(${JSON.stringify(item)})'>Edit</button>
                    <button class="action-btn delete-btn" onclick='deleteRoute(${item.item_id})'>Delete</button>
                `;
            }
        }

        row.innerHTML = `
            <td>${item.item_type}</td>
            <td>${item.item_id}</td>
            <td>${item.col1}</td>
            <td>${item.col2}</td>
            <td>${formatTime(item.departure_time)}</td>
            <td>${formatTime(item.arrival_time)}</td>
            ${isAdminPage() ? `<td>${actions}</td>` : ""}
        `;
        tbody.appendChild(row);
    });
}

async function saveBus() {
    const busId = document.getElementById("bus_id").value;
    const payload = {
        bus_number: document.getElementById("bus_number").value,
        capacity: document.getElementById("capacity").value,
        departure_time: document.getElementById("bus_departure_time").value,
        arrival_time: document.getElementById("bus_arrival_time").value
    };

    const url = busId ? `/update_bus/${busId}` : "/add_bus";
    const method = busId ? "PUT" : "POST";

    await fetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });

    resetBusForm();
    await loadCombinedData();
    await loadAnalytics();
}

function editBus(item) {
    document.getElementById("bus_id").value = item.item_id;
    document.getElementById("bus_number").value = item.col1;
    document.getElementById("capacity").value = item.col2;
    document.getElementById("bus_departure_time").value = formatTime(item.departure_time);
    document.getElementById("bus_arrival_time").value = formatTime(item.arrival_time);
    window.scrollTo({ top: 0, behavior: "smooth" });
}

function resetBusForm() {
    const ids = ["bus_id", "bus_number", "capacity", "bus_departure_time", "bus_arrival_time"];
    ids.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = "";
    });
}

async function deleteBus(busId) {
    if (!confirm("Delete this bus?")) return;
    await fetch(`/delete_bus/${busId}`, { method: "DELETE" });
    await loadCombinedData();
    await loadAnalytics();
}

async function saveRoute() {
    const routeId = document.getElementById("route_id").value;
    const payload = {
        source: document.getElementById("source").value,
        destination: document.getElementById("destination").value,
        departure_time: document.getElementById("route_departure_time").value,
        arrival_time: document.getElementById("route_arrival_time").value
    };

    const url = routeId ? `/update_route/${routeId}` : "/add_route";
    const method = routeId ? "PUT" : "POST";

    await fetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });

    resetRouteForm();
    await loadCombinedData();
    await loadAnalytics();
}

function editRoute(item) {
    document.getElementById("route_id").value = item.item_id;
    document.getElementById("source").value = item.col1;
    document.getElementById("destination").value = item.col2;
    document.getElementById("route_departure_time").value = formatTime(item.departure_time);
    document.getElementById("route_arrival_time").value = formatTime(item.arrival_time);
    window.scrollTo({ top: 0, behavior: "smooth" });
}

function resetRouteForm() {
    const ids = ["route_id", "source", "destination", "route_departure_time", "route_arrival_time"];
    ids.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = "";
    });
}

async function deleteRoute(routeId) {
    if (!confirm("Delete this route?")) return;
    await fetch(`/delete_route/${routeId}`, { method: "DELETE" });
    await loadCombinedData();
    await loadAnalytics();
}

async function loadAnalytics() {
    const analytics = await getJSON("/analytics");

    const totalBuses = document.getElementById("totalBuses");
    const totalRoutes = document.getElementById("totalRoutes");
    const totalLogins = document.getElementById("totalLogins");
    const avgCapacity = document.getElementById("avgCapacity");

    if (totalBuses) totalBuses.textContent = analytics.total_buses ?? 0;
    if (totalRoutes) totalRoutes.textContent = analytics.total_routes ?? 0;
    if (totalLogins) totalLogins.textContent = analytics.total_logins ?? 0;
    if (avgCapacity) avgCapacity.textContent = analytics.avg_capacity ?? 0;

    renderCharts(analytics);
}

function renderCharts(data) {
    const loginCanvas = document.getElementById("loginChart");
    const userCanvas = document.getElementById("userChart");

    if (loginCanvas) {
        if (loginChartInstance) loginChartInstance.destroy();
        loginChartInstance = new Chart(loginCanvas, {
            type: "bar",
            data: {
                labels: data.login_by_hour.map(x => `${x.login_hour}:00`),
                datasets: [{
                    label: "Logins",
                    data: data.login_by_hour.map(x => x.count)
                }]
            }
        });
    }

    if (userCanvas) {
        if (userChartInstance) userChartInstance.destroy();
        userChartInstance = new Chart(userCanvas, {
            type: "doughnut",
            data: {
                labels: data.top_users.map(x => x.username),
                datasets: [{
                    label: "Top Users",
                    data: data.top_users.map(x => x.login_count)
                }]
            }
        });
    }
}

async function predictDelay() {
    const payload = {
        traffic: document.getElementById("traffic").value,
        distance: document.getElementById("distance").value,
        weather: document.getElementById("weather").value
    };

    const res = await fetch("/predict_delay", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });
    const data = await res.json();

    document.getElementById("predictionResult").textContent =
        `Predicted Delay: ${data.predicted_delay_minutes} minutes`;
}

window.onload = async function () {
    await loadCombinedData();
    await loadAnalytics();
};