from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import *
from .networking import * # Aqui se mandan los comandos de red por SSH

def multilayer_HTML(request, id):
    interfaces = Interface.objects.filter(device=id)
    context = {
        'id': id,
        'interfaces': interfaces
    }
    return render(request, "SWD.html", context)

def access_HTML(request, id): 
    interfaces = Interface.objects.filter(device=id)
    context = {
        'id': id,
        'interfaces': interfaces
    }
    return render(request, 'access.html', context)

def index_HTML(request):
    return render(request, 'index.html')

def create_vlan(request, id):
    if request.method != 'POST': # Si el metodo de carga no es POST, redirigimos a la carga del HTML
        return redirect('multilayer', id)
    
    vlan_id = request.POST.get('numVLAN')  # Recibir los datos del formulario
    vlan_name = request.POST.get('nomVLAN') # get() consigue el dato del input con el name='' del html

    # Crear la vlan en la base de datos
    vlan, created = Vlan.objects.get_or_create(
        vlan_id=vlan_id,
        defaults={'name': vlan_name}
    )

    # Enviar el comando para crear la vlan via SSH al multicapa con ese ID
    create_vlan_ssh(id, vlan_id)

    # Volvemos a rendereizar la pantalla de donde viene se envio el form
    return redirect('multilayer', id)

def delete_vlan(request, id):
    if request.method != 'POST': # Si el metodo de carga no es POST, redirigimos a la carga del HTML
        return redirect('multilayer', id)
    
    vlan_id = request.POST.get('numVLANElim') # get() consigue el dato del input con el name='' del html
    if vlan_id == 2:
        return redirect('multilayer', id)
    # Conseguir la VLAN de la base de datos
    vlan = get_object_or_404(Vlan, vlan_id=vlan_id)
    # Mandar el comando de eliminacion al multicapa
    delete_vlan_ssh(id, vlan_id)
    # Eliminar la VLAN de la base de datos
    vlan.delete()
    return redirect('multilayer', id)


def hub_form_access(request, id):
    return redirect('access', id)


def assign_vlan(id):
    if request.method != 'POST': # Si el metodo de carga no es POST, redirigimos a la carga del HTML
        return redirect('access', id)

    type = request.POST.get('tipo')
    vlan_id = request.POST.get('vlanAcceso')
    start = request.POST.get('intRangInicio')
    end = request.POST.get('intRangFin')
    print(type, vlan_id, start, end)

    if vlan_id == 2 or vlan_id == 1:
        return redirect('access', id)
    vlan = get_object_or_404(Vlan, vlan_id=vlan_id)
    device = get_object_or_404(Device, pk=id)
    print(vlan, device)
    # Ir recorriendo el rango de interfaces y asignandoles la VLAN
    for i in range(int(start), int(end)+1):
        interface_name = f"FastEthernet0/{i}"
        #Verificar que la interfaz existe
        interface = get_object_or_404(Interface, device_id=id, name=interface_name)
        print(interface)
        # Asignar la VLAN a la interfaz en la base de datos
        Vlan_IntAssignment.objects.get_or_create(
            interface=interface,
            vlan=vlan,
            defaults={'is_native': False}
        )

        # Mandar el comando de asignacion via SSH al switch de acceso
        assign_vlan_ssh(id, interface_name, vlan_id, type)

        # Refrescar la IP del host conectado despues del cambio
        refresh_host_for_interface(device, interface)


def change_port_status(id):
    if request.method != 'POST': # Si el metodo de carga no es POST, redirigimos a la carga del HTML
        return redirect('access', id)

    type = request.POST.get('tipoIntRango')
    on = request.POST.get('OnRango')
    start = request.POST.get('intRangInicio')
    end = request.POST.get('intRangFin')

    status = status == 'on'
    for i in range(int(start), int(end)+1):
        print(status == 'on')
        interface_name = f"FastEthernet0/{i}"

        print(interface_name)
        change_port_status_ssh(id, interface_name, status)


def switches_status(request):
    #Acceder a todos los switches en la base de datos
    switches = Device.objects.filter(device_type='switch')
    data = []

    #Acceder a las interfaces de cada switch
    for d in switches:
        interfaces = d.interfaces.all()
        device_data = {
            'device_id': d.pk,
            'hostname': d.hostname,
            'interfaces': [
                {'name': inter.name, 'state': inter.state} for inter in interfaces
            ]
        }
        data.append(device_data)
    return JsonResponse(data, safe=False)

def polling_interfaces(request, id):
    interfaces = Interface.objects.select_related('device').filter(device__id=id)

    data = []
    for iface in interfaces:
        data.append({
            'name': iface.name,
            'state': iface.state,
            'is_access': iface.is_access,
        })
    
    return JsonResponse({'interfaces': data}, safe=False)


