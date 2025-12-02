
    // ELEMENTOS PRINCIPALES
    const divInterfaces = document.getElementById('interfaces');
    const divVlans = document.getElementById('vlans');
    
        
    // Elementos de la sección de Interfaces
    const menuInterfaces = document.getElementById('interface-type-menu');
    const btnUnica = document.getElementById('btn-unica');
    const btnRango = document.getElementById('btn-rango');

    const configUnica = document.getElementById('config-unica');
    const configRango = document.getElementById('config-rango');

    const configDisponible = document.getElementById('config-disponible');
    const configDisponibleRange = document.getElementById('range-config-disponible');

    const btnSiguienteUnica = document.getElementById('btn-siguiente-unica');
    const btnSiguienteRango = document.getElementById('btn-siguiente-rango');

    // Muestra la configuración UNICA
    btnUnica.addEventListener('click', () => {
        menuInterfaces.classList.add('hidden');

        configRango.classList.add('hidden');
        configDisponibleRange.classList.add('hidden'); // Oculta la del rango

        configUnica.classList.remove('hidden');
        configDisponible.classList.add('hidden'); // Oculta la disponible única
    });

    // Muestra la configuración RANGO
    btnRango.addEventListener('click', () => {
        menuInterfaces.classList.add('hidden');

        configUnica.classList.add('hidden');
        configDisponible.classList.add('hidden'); // Oculta la de única

        configRango.classList.remove('hidden');
        configDisponibleRange.classList.add('hidden'); // Oculta la disponible rango
    });

    // Acción para botones "SIGUIENTE"
    btnSiguienteUnica.addEventListener('click', () => {
        configDisponible.classList.remove('hidden');
    });

    btnSiguienteRango.addEventListener('click', () => {
        configDisponibleRange.classList.remove('hidden');
    });
    

    // Acción para botones "REGRESAR"
    document.querySelectorAll('.btn-regresar').forEach(btn => {
        btn.addEventListener('click', () => {
            configUnica.classList.add('hidden');
            configRango.classList.add('hidden');

            configDisponible.classList.add('hidden');
            configDisponibleRange.classList.add('hidden');

            menuInterfaces.classList.remove('hidden');
        });
    });

    // Elementos de la sección de VLANs
    const menuVlans = document.getElementById('vlan-type-menu');
    const btnCrearVlan = document.getElementById('btn-crear-vlan');
    const btnEliminarVlan = document.getElementById('btn-eliminar-vlan');
    const configCrearVlan = document.getElementById('config-crear-vlan');
    const configEliminarVlan = document.getElementById('config-eliminar-vlan');
    
    // Muestra la configuración CREAR VLAN
    btnCrearVlan.addEventListener('click', () => {
        menuVlans.classList.add('hidden');
        configEliminarVlan.classList.add('hidden');
        configCrearVlan.classList.remove('hidden');
    });

    // Muestra la configuración ELIMINAR VLAN
    btnEliminarVlan.addEventListener('click', () => {
        menuVlans.classList.add('hidden');
        configCrearVlan.classList.add('hidden');
        configEliminarVlan.classList.remove('hidden');
    });

    // Acción para botones "REGRESAR" de VLANs (Vuelve al menú Crear/Eliminar)
    document.querySelectorAll('.btn-vlan-regresar').forEach(btn => {
        btn.addEventListener('click', () => {
            configCrearVlan.classList.add('hidden');
            configEliminarVlan.classList.add('hidden');
            menuVlans.classList.remove('hidden'); // Vuelve a mostrar el menú Crear/Eliminar
        });
    });

    
    
    // Asegúrate de que las IDs de estos botones estén configuradas en tu HTML principal
    const btnShowInterfaces = document.getElementById('btn-show-interfaces');
    const btnShowVlans = document.getElementById('btn-show-vlans');

    if (btnShowInterfaces && btnShowVlans) {
        btnShowInterfaces.addEventListener('click', () => {
            divInterfaces.classList.remove('hidden');
            divVlans.classList.add('hidden');
            // Asegura que las sub-secciones internas empiecen en el menú de selección
            configUnica.classList.add('hidden');
            configRango.classList.add('hidden');
            configDisponible.classList.add('hidden');
            menuInterfaces.classList.remove('hidden');
        });

        btnShowVlans.addEventListener('click', () => {
            divVlans.classList.remove('hidden');
            divInterfaces.classList.add('hidden');
            // Asegura que las sub-secciones internas empiecen en el menú de selección
            configCrearVlan.classList.add('hidden');
            configEliminarVlan.classList.add('hidden');
            menuVlans.classList.remove('hidden');
        });
    }



