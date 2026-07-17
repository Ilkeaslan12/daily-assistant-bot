const API_BASE_URL =
    window.location.hostname === "localhost"
        ? "http://127.0.0.1:8000"
        : "";

function formatDate(dateValue) {
    if (!dateValue) {
        return "-";
    }

    return new Date(dateValue).toLocaleString("tr-TR");
}

function createCell(value, className = "") {
    const cell = document.createElement("td");
    cell.textContent = value ?? "-";

    if (className) {
        cell.className = className;
    }

    return cell;
}

function renderChats(chats) {
    const chatTable = document.getElementById("chatTable");
    const chatEmpty = document.getElementById("chatEmpty");
    const tableWrapper = chatTable.closest(".table-wrapper");

    chatTable.innerHTML = "";

    if (!chats.length) {
        tableWrapper.style.display = "none";
        chatEmpty.style.display = "block";
        return;
    }

    tableWrapper.style.display = "block";
    chatEmpty.style.display = "none";

    chats.forEach((chat) => {
        const row = document.createElement("tr");

        row.appendChild(createCell(formatDate(chat.created_at)));
        row.appendChild(createCell(chat.user_message));
        row.appendChild(createCell(chat.bot_response));

        chatTable.appendChild(row);
    });
}

function renderErrors(errors) {
    const errorTable = document.getElementById("errorTable");
    const errorEmpty = document.getElementById("errorEmpty");
    const tableWrapper = errorTable.closest(".table-wrapper");

    errorTable.innerHTML = "";

    if (!errors.length) {
        tableWrapper.style.display = "none";
        errorEmpty.style.display = "block";
        return;
    }

    tableWrapper.style.display = "block";
    errorEmpty.style.display = "none";

    errors.forEach((error) => {
        const row = document.createElement("tr");
        const typeCell = document.createElement("td");
        const badge = document.createElement("span");

        badge.className = "error-badge";
        badge.textContent = error.error_type ?? "UnknownError";

        typeCell.appendChild(badge);

        row.appendChild(createCell(formatDate(error.created_at)));
        row.appendChild(typeCell);
        row.appendChild(createCell(error.error_message));

        errorTable.appendChild(row);
    });
}

async function loadDashboard() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/admin`);

        if (!response.ok) {
            throw new Error(`Request failed with status ${response.status}`);
        }

        const data = await response.json();

        if (data.status !== "success") {
            throw new Error(data.message || "Dashboard could not be loaded.");
        }

        document.getElementById("totalMessages").textContent =
            data.statistics.total_messages ?? 0;

        document.getElementById("totalErrors").textContent =
            data.statistics.total_errors ?? 0;

        renderChats(data.recent_chats ?? []);
        renderErrors(data.recent_errors ?? []);
    } catch (error) {
        console.error(error);
        alert("Dashboard could not be loaded.");
    }
}

loadDashboard();