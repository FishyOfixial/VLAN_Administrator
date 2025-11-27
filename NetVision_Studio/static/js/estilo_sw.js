// ELEMENTOS PRINCIPALES
const divInterfaces = document.getElementById('interfaces');

// **********************************************
// LÓGICA DE INTERFACES
// **********************************************

// Elementos de la sección de Interfaces
const menuInterfaces = document.getElementById('interface-type-menu');
const btnUnica = document.getElementById('btn-unica');
const btnRango = document.getElementById('btn-rango');
const configUnica = document.getElementById('config-unica');
const configRango = document.getElementById('config-rango');
const configDisponible = document.getElementById('config-disponible');
const btnSiguienteUnica = document.getElementById('btn-siguiente-unica');
const btnSiguienteRango = document.getElementById('btn-siguiente-rango');

// Muestra la configuración UNICA
if (btnUnica) {
    btnUnica.addEventListener('click', () => {
        menuInterfaces.classList.add('hidden');
        configRango.classList.add('hidden'); // Asegura que el otro esté oculto
        configUnica.classList.remove('hidden');
        configDisponible.classList.add('hidden'); // Oculta las disponibles al volver a empezar
    });
}

// Muestra la configuración RANGO
if (btnRango) {
    btnRango.addEventListener('click', () => {
        menuInterfaces.classList.add('hidden');
        configUnica.classList.add('hidden'); // Asegura que el otro esté oculto
        configRango.classList.remove('hidden');
        configDisponible.classList.add('hidden'); // Oculta las disponibles al volver a empezar
    });
}

// Acción para botones "SIGUIENTE" (Muestra Configuraciones Disponibles)
if (btnSiguienteUnica) {
    btnSiguienteUnica.addEventListener('click', () => {
        configDisponible.classList.remove('hidden');
    });
}
if (btnSiguienteRango) {
    btnSiguienteRango.addEventListener('click', () => {
        configDisponible.classList.remove('hidden');
    });
}


// Acción para botones "REGRESAR" (Vuelve al menú de Interfaces)
document.querySelectorAll('.btn-regresar').forEach(btn => {
    btn.addEventListener('click', () => {
        configUnica.classList.add('hidden');
        configRango.classList.add('hidden');
        configDisponible.classList.add('hidden');
        menuInterfaces.classList.remove('hidden'); // Vuelve a mostrar el menú Interfaz Unica/Rango
    });
});


// **********************************************
// LÓGICA DE MENÚ PRINCIPAL
// **********************************************

// Aquí solo manejamos el botón que existe: "Ingresar a interfaces"
const btnShowInterfaces = document.getElementById('btn-show-interfaces');

if (btnShowInterfaces) {
    btnShowInterfaces.addEventListener('click', () => {
        divInterfaces.classList.remove('hidden');

        // Asegura que las sub-secciones internas empiecen en el menú de selección
        configUnica.classList.add('hidden');
        configRango.classList.add('hidden');
        configDisponible.classList.add('hidden');
        menuInterfaces.classList.remove('hidden');
    });
}