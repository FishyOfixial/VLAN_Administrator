// Estado local de switches
let switches = [];

// Función para actualizar switches desde el backend
async function fetchSwitchesStatus() {
    try {
        const response = await fetch('/api/switches/status/');
        const data = await response.json();

        // Actualizamos la variable switches
        switches = data;

        // Renderizamos la UI
        renderSwitches();
    } catch (err) {
        console.error('Error al obtener el estado de switches:', err);
    }
}

// Función para renderizar los switches en la página
function renderSwitches() {
    const container = document.getElementById('switches-container');
    container.innerHTML = ''; // Limpiar el contenedor

    switches.forEach(sw => {
        const div = document.createElement('div');
        div.classList.add('switch');
        div.innerHTML = `<h3>${sw.hostname}</h3>`;

        const ul = document.createElement('ul');
        sw.interfaces.forEach(iface => {
            const li = document.createElement('li');
            li.textContent = `${iface.name}: ${iface.state ? 'UP' : 'DOWN'}`;
            li.style.color = iface.state ? 'green' : 'red';
            ul.appendChild(li);
        });

        div.appendChild(ul);
        container.appendChild(div);
    });
}

// Polling cada 5 segundos
fetchSwitchesStatus(); // fetch inicial
setInterval(fetchSwitchesStatus, 5000);