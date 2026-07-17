const API_BASE_URL =
    window.location.hostname === "localhost"
        ? "http://127.0.0.1:8000"
        : "";

async function loadDashboard() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/admin`);
        const data = await response.json();

        if (data.status !== "success") {
            alert("Dashboard could not be loaded.");
            return;
        }

        document.getElementById("totalMessages").textContent =
            data.statistics.total_messages;

        document.getElementById("totalErrors").textContent =
            data.statistics.total_errors;

        const chatTable = document.getElementById("chatTable");
        chatTable.innerHTML = "";

        data.recent_chats.forEach(chat => {
            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${new Date(chat.created_at).toLocaleString()}</td>
                <td>${chat.user_message}</td>
                <td>${chat.bot_response}</td>
            `;

            chatTable.appendChild(row);
        });

        const errorTable = document.getElementById("errorTable");
        errorTable.innerHTML = "";

        data.recent_errors.forEach(error => {
            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${new Date(error.created_at).toLocaleString()}</td>
                <td>${error.error_type}</td>
                <td>${error.error_message}</td>
            `;

            errorTable.appendChild(row);
        });

    } catch (error) {
        console.error(error);
        alert("Unable to connect to the server.");
    }
}

loadDashboard();