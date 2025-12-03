from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from .models import *
from .networking import *

def multilayer_HTML(request, id):
    interfaces = Interface.objects.filter(device=id)
    actVlans = Vlan.objects.all()

    if not interfaces.exists():
        messages.error(request, "No se encontraron interfaces para este dispositivo.")
    if not actVlans.exists():
        messages.error(request, "No se encontraron VLANs registradas.")

    context = {
        'id': id,
        'interfaces': interfaces,
        'actVlans': actVlans
    }
    return render(request, "SWD.html", context)

def access_HTML(request, id): 
    interfaces = Interface.objects.filter(device=id)
    if not interfaces.exists():
        messages.error(request, "No se encontraron interfaces para este dispositivo.")

    context = {
        'id': id,
        'interfaces': interfaces
    }
    return render(request, 'access.html', context)

def index_HTML(request):
    return render(request, 'index.html')

def create_vlan(request, id):
    if request.method != 'POST':
        return redirect('multilayer', id)
    
    vlan_id = request.POST.get('numVLAN')
    vlan_name = request.POST.get('nomVLAN')

    if not vlan_id or not vlan_name:
        messages.error(request, "No se recibieron datos para crear la VLAN.")
        return redirect('multilayer', id)

    try:
        create_vlan_ssh(id, vlan_id)
    except Exception:
        messages.error(request, "No se pudo crear la VLAN en el switch via SSH.")
        return redirect('multilayer', id)
    
    try:
        vlan, created = Vlan.objects.get_or_create(
            vlan_id=vlan_id,
            defaults={'name': vlan_name}
        )
    except Exception:
        messages.error(request, "Error al crear la VLAN en la base de datos.")
        return redirect('multilayer', id)

    messages.success(request, "Operación realizada correctamente.")
    return redirect('multilayer', id)

def delete_vlan(request, id):
    if request.method != 'POST':
        return redirect('multilayer', id)
    
    vlan_id = request.POST.get('numVLANElim')
    if not vlan_id:
        messages.error(request, "No se envió un ID de VLAN para eliminar.")
        return redirect('multilayer', id)

    if vlan_id == "2":
        messages.error(request, "La VLAN 2 no puede ser eliminada.")
        return redirect('multilayer', id)

    try:
        vlan = get_object_or_404(Vlan, vlan_id=vlan_id)
    except:
        messages.error(request, "La VLAN especificada no existe.")
        return redirect('multilayer', id)

    try:
        delete_vlan_ssh(id, vlan_id)
    except Exception:
        messages.error(request, "No se pudo eliminar la VLAN del switch via SSH.")
        return redirect('multilayer', id)

    try:
        vlan.delete()
    except:
        messages.error(request, "Error al eliminar la VLAN de la base de datos.")
        return redirect('multilayer', id)

    messages.success(request, "Operación realizada correctamente.")
    return redirect('multilayer', id)

def hub_form_access(request, id, mode):
    if request.method != 'POST':
        return redirect('access', id)
    
    start = end = iface = None

    if mode == 'range':
        start = request.POST.get("intRangInicio")
        end = request.POST.get("intRangFin")
        if not start or not end:
            messages.error(request, "Datos incompletos para el rango de interfaces.")
            return redirect('access', id)

    elif mode == 'unique':
        iface = request.POST.get('numInterfaz')
        if not iface:
            messages.error(request, "No se recibió la interfaz única.")
            return redirect('access', id)

    status = request.POST.get("estado")
    vlan_id = request.POST.get("vlanAcceso")

    if status is not None:
        try:
            status = status == 'OnRango'
            if mode == 'range':
                change_port_status(request, start, end, status, id)
            elif mode == 'unique':
                change_port_status(request, iface, iface, status, id)
        except Exception:
            messages.error(request, "Error al cambiar el estado de los puertos.")
            return redirect('multilayer', id)

    if vlan_id != "":
        try:
            if mode == 'range':
                assign_vlan(request, start, end, vlan_id, id)
            elif mode == 'unique':
                assign_vlan(request, iface, iface, vlan_id, id)
        except Exception:
            messages.error(request, "Error al asignar VLAN a las interfaces.")
            return redirect('multilayer', id)

    return redirect('access', id)

def assign_vlan(request, start, end, vlan_id, id):

    if vlan_id in ("1", "2"):
        messages.error(request, "La VLAN 1 y 2 no pueden asignarse.")
        return redirect('access', id)

    try:
        vlan = get_object_or_404(Vlan, vlan_id=vlan_id)
        device = get_object_or_404(Device, pk=id)
    except:
        messages.error(request, "No se encontró el dispositivo o la VLAN.")
        return redirect('access', id)

    for i in range(int(start), int(end)+1):
        interface_name = f"FastEthernet0/{i}"

        try:
            interface = get_object_or_404(Interface, device_id=id, name=interface_name)
        except:
            messages.error(request, f"No existe la interfaz {interface_name}.")
            continue

        try:
            Vlan_IntAssignment.objects.get_or_create(interface=interface, vlan=vlan)
            assign_vlan_ssh(id, interface.name, vlan.vlan_id)
            refresh_host_for_interface(device, interface)
        except:
            messages.error(request, f"No se pudo asignar la VLAN a la interfaz {interface_name}.")
            return redirect('access', id)

    messages.success(request, "Operación realizada correctamente.")
    return

def change_port_status(request, start, end, status, id):

    for i in range(int(start), int(end)+1):
        interface_name = f"FastEthernet0/{i}"

        try:
            change_port_status_ssh(id, interface_name, status)
        except Exception:
            messages.error(request, f"No se pudo cambiar el estado de {interface_name}.")
            return redirect('access', id)

    messages.success(request, "Operación realizada correctamente.")
    return

def polling_interfaces(request, id):
    interfaces = Interface.objects.select_related('device').filter(device__id=id)

    if not interfaces.exists():
        return JsonResponse({'error': 'No se encontraron interfaces para este dispositivo.'}, status=404)

    data = []
    for iface in interfaces:
        data.append({
            'name': iface.name,
            'state': iface.state,
            'is_access': iface.is_access,
        })
    
    return JsonResponse({'interfaces': data})
