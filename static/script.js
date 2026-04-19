let combinedData = [];
let loginChartInstance = null;
let userChartInstance = null;

async function getJSON(url) {
    const res = await fetch(url);
    if (!res.ok) {
        throw new Error(`Request failed: ${url}`);
    }
    return await res.json();
}

function isAdminPage() {
    return window.location.pathname === "/admin";
}

function formatTime(value) {
    if (!value) return "-";
    return String(value).slice(0, 5);
}

function safeText(value) {
    if (value === null || value === undefined) return "";
    return String(value);
}

async function loadCombinedData() {
    try {
        combinedData = await getJSON("/combined_data");
        console.log("combinedData:", combinedData);
        renderCombinedTable();
    } catch (err) {
        console.error("Combined data load error:", err);
    }
}

function renderCombinedTable() {
    const tbody = document.getElementById("combinedTableBody");
    if (!tbody) return;

    const searchValue = safeText(document.getElementById("searchInput")?.value).trim().toLowerCase();
    const typeValue = document.getElementById("typeFilter")?.value || "All";

    tbody.innerHTML = "";

    const filtered = combinedData.filter(item => {
        const itemType = safeText(item.item_type);
        const itemId = safeText(item.item_id);
        const value1 = safeText(item.value_1);
        const value2 = safeText(item.value_2);
        const dep = formatTime(item.departure_time);
        const arr = formatTime(item.arrival_time);

        const matchesType = typeValue === "All" || itemType === typeValue;
        const searchText = `${itemType} ${itemId} ${value1} ${value2} ${dep} ${arr}`.toLowerCase();
        const matchesSearch = searchValue === "" || searchText.includes(searchValue);

        return matchesType && matchesSearch;
    });

    if (filtered.length === 0) {
        const colspan = isAdminPage() ? 7 : 6;
        tbody.innerHTML = `<tr><td colspan="${colspan}" style="text-align:center;">No matching data found</td></tr>`;
        return;
    }

    filtered.forEach(item => {
        const itemType = safeText(item.item_type);
        const itemId = safeText(item.item_id);
        const value1 = safeText(item.value_1);
        const value2 = safeText(item.value_2);
        const dep = formatTime(item.departure_time);
        const arr = formatTime(item.arrival_time);

        const row = document.createElement("tr");

        let actions = "";
        if (isAdminPage()) {
            if (itemType === "Bus") {
                actions = `
                    <button class="action-btn edit-btn" onclick='editBus(${JSON.stringify(item)})'>Edit</button>
                    <button class="action-btn delete-btn" onclick='deleteBus(${itemId})'>Delete</button>
                `;
            } else {
                actions = `
                    <button class="action-btn edit-btn" onclick='editRoute(${JSON.stringify(item)})'>Edit</button>
                    <button class="action-btn delete-btn" onclick='deleteRoute(${itemId})'>Delete</button>
                `;
            }
        }

        row.innerHTML = `
            <td>${itemType}</td>
            <td>${itemId}</td>
            <td>${value1}</td>
            <td>${value2}</td>
            <td>${dep}</td>
            <td>${arr}</td>
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
    if (isAdminPage()) await loadAnalytics();
}

function editBus(item) {
    document.getElementById("bus_id").value = item.item_id;
    document.getElementById("bus_number").value = item.value_1;
    document.getElementById("capacity").value = item.value_2;
    document.getElementById("bus_departure_time").value = formatTime(item.departure_time);
    document.getElementById("bus_arrival_time").value = formatTime(item.arrival_time);
    window.scrollTo({ top: 0, behavior: "smooth" });
}

function resetBusForm() {
    ["bus_id", "bus_number", "capacity", "bus_departure_time", "bus_arrival_time"].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = "";
    });
}

async function deleteBus(busId) {
    if (!confirm("Delete this bus?")) return;
    await fetch(`/delete_bus/${busId}`, { method: "DELETE" });
    await loadCombinedData();
    if (isAdminPage()) await loadAnalytics();
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
    if (isAdminPage()) await loadAnalytics();
}

function editRoute(item) {
    document.getElementById("route_id").value = item.item_id;
    document.getElementById("source").value = item.value_1;
    document.getElementById("destination").value = item.value_2;
    document.getElementById("route_departure_time").value = formatTime(item.departure_time);
    document.getElementById("route_arrival_time").value = formatTime(item.arrival_time);
    window.scrollTo({ top: 0, behavior: "smooth" });
}

function resetRouteForm() {
    ["route_id", "source", "destination", "route_departure_time", "route_arrival_time"].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = "";
    });
}

async function deleteRoute(routeId) {
    if (!confirm("Delete this route?")) return;
    await fetch(`/delete_route/${routeId}`, { method: "DELETE" });
    await loadCombinedData();
    if (isAdminPage()) await loadAnalytics();
}

async function loadAnalytics() {
    if (!isAdminPage()) return;

    try {
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
    } catch (err) {
        console.error("Analytics load error:", err);
    }
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
    if (isAdminPage()) {
        await loadAnalytics();
    }
};