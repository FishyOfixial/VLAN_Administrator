from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import *
from .networking import * # Aqui se mandan los comandos de red por SSH

def multilayer_HTML(request, id):
    context = {
        'id': id
    }
    return render(request, "SWD.html", context)

def access_HTML(request): 
    return render(request, 'access.html')

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
    add_vlan(id, vlan_id)

    # Volvemos a rendereizar la pantalla de donde viene se envio el form
    return redirect('multilayer', id)


def delete_vlan(request, id):
    if request.method != 'POST': # Si el metodo de carga no es POST, redirigimos a la carga del HTML
        return redirect('multilayer', id)
    
    vlan_id = request.POST.get('numVLANElim') # get() consigue el dato del input con el name='' del html
    
    # Conseguir la VLAN de la base de datos
    vlan = get_object_or_404(Vlan, vlan_id=vlan_id)
    # Mandar el comando de eliminacion al multicapa
    delete_vlan(id, vlan_id)
    # Eliminar la VLAN de la base de datos
    vlan.delete()

def assign_vlan(request, id):
    if request.method != 'POST': # Si el metodo de carga no es POST, redirigimos a la carga del HTML
        return redirect('access', id)

    type = request.POST.get('tipoIntRango')
    vlan_id = request.POST.get('vlanAcceso')
    start = request.POST.get('intRangInicio')
    end = request.POST.get('intRangFin')

    vlan = get_object_or_404(Vlan, vlan_id=vlan_id)
    
    # Ir recorriendo el rango de interfaces y asignandoles la VLAN
    for i in range(int(start), int(end)+1):
        interface_name = f"fa0/{i}"
        #Verificar que la interfaz existe
        interface = get_object_or_404(Interface, device_id=id, name=interface_name)

        # Asignar la VLAN a la interfaz en la base de datos
        Vlan_IntAssignment.objects.get_or_create(
            interface=interface,
            vlan=vlan,
            defaults={'is_native': type == 'native'}
        )

        # Mandar el comando de asignacion via SSH al switch de acceso
        assign_vlan_to_interface(id, interface_name, vlan_id, type)
    



def switches_status(request):
    switches = Device.objects.filter(device_type='switch')
    data = []

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