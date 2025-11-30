// ELEMENTOS PRINCIPALES
const divInterfaces = document.getElementById('interfaces');

const menuInterfaces = document.getElementById('interface-type-menu');
const btnUnica = document.getElementById('btn-unica');
const btnRango = document.getElementById('btn-rango');

const configUnica = document.getElementById('config-unica');
const configRango = document.getElementById('config-rango');

const configDisponible = document.getElementById('config-disponible');
const configDisponibleRange = document.getElementById('range-disp-config');

const btnSiguienteUnica = document.getElementById('btn-siguiente-unica');
const btnSiguienteRango = document.getElementById('btn-siguiente-rango');

// Muestra configuración única
btnUnica.addEventListener('click', () => {
    menuInterfaces.classList.add('hidden');

    configRango.classList.add('hidden');
    configDisponibleRange.classList.add('hidden'); 

    configUnica.classList.remove('hidden');
    configDisponible.classList.add('hidden');
});

// Muestra configuración rango
btnRango.addEventListener('click', () => {
    menuInterfaces.classList.add('hidden');

    configUnica.classList.add('hidden');
    configDisponible.classList.add('hidden');

    configRango.classList.remove('hidden');
    configDisponibleRange.classList.add('hidden');
});

// Botones "Siguiente"
btnSiguienteUnica.addEventListener('click', () => {
    configDisponible.classList.remove('hidden');
});

btnSiguienteRango.addEventListener('click', () => {
    configDisponibleRange.classList.remove('hidden');
});

// Botones "Regresar"
document.querySelectorAll('.btn-regresar').forEach(btn => {
    btn.addEventListener('click', () => {
        configUnica.classList.add('hidden');
        configRango.classList.add('hidden');

        configDisponible.classList.add('hidden');
        configDisponibleRange.classList.add('hidden');

        menuInterfaces.classList.remove('hidden');
    });
});

const btnShowInterfaces = document.getElementById('btn-show-interfaces');


btnShowInterfaces.addEventListener('click', () => {
    divInterfaces.classList.remove('hidden');
    // Asegura que las sub-secciones internas empiecen en el menú de selección
    configUnica.classList.add('hidden');
    configRango.classList.add('hidden');
    configDisponible.classList.add('hidden');
    menuInterfaces.classList.remove('hidden');
});
    
