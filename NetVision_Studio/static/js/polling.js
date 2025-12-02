document.addEventListener("DOMContentLoaded", () => {
    initPolling();
});

function initPolling() {
    const container = document.getElementById('div-console');

    if (!container) return;

    async function fetchSwitchInterfaces() {
        try {
            const response = await fetch(`/poll/interfaces/${deviceId}/`);
            const data = await response.json();
            renderInterfaces(data.interfaces);
        } catch (err) {
            console.error('Error obteniendo interfaces:', err);
        }
    }

    function renderInterfaces(interfaces) {
        let listContainer = document.getElementById('interfaces-list');

        // Si no existe el contenedor lo creamos SOLO una vez
        if (!listContainer) {
            listContainer = document.createElement("div");
            listContainer.id = "interfaces-list";
            container.appendChild(listContainer);
        }

        listContainer.innerHTML = "";

        interfaces.forEach(iface => {
            if (!iface.state) return;

            const div = document.createElement("div");
            div.className = "console-entry";

            div.innerHTML = `
                <h3>Interfaz ${iface.name} 🟢</h3>
                <pre>${iface.is_access ? "Acceso" : "Troncal"}</pre>
            `;

            listContainer.appendChild(div);
        });
    }

    fetchSwitchInterfaces();
    setInterval(fetchSwitchInterfaces, 5000);
}
