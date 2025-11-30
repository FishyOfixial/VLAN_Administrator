import time
from .models import Device, Vlan, Interface, Host
from .ssh_client import SSHClient
from .syslog.utils import *

# Función privada para evitar repetir código.
# Se conecta al dispositivo, manda comandos y regresa la respuesta.
def _run_vlan_command(device_id, commands):
    device = Device.objects.get(id=device_id)

    client = SSHClient(
        hostname=device.hostname,
        ip=device.ip_address,
        username=device.username,
        password=device.password,
        device_type='cisco_ios'
    )

    client.connect()
    output = client.send_config(commands)  # Ejecuta los comandos
    client.close()
    return output


# Crear VLAN en el dispositivo
def create_vlan_ssh(device_id, vlan_id):
    vlan = Vlan.objects.get(vlan_id=vlan_id)

    commands = [
        f"vlan {vlan.vlan_id}",
        f"name {vlan.name}",
        "exit"
    ]

    return _run_vlan_command(device_id, commands)


# Borrar VLAN del dispositivo
def delete_vlan_ssh(device_id, vlan_id):
    commands = [
        f"no vlan {vlan_id}",
        "exit"
    ]

    return _run_vlan_command(device_id, commands)

def assign_vlan_ssh(id, interface_name, vlan_id, type):
    if type == 'access':
        commands = [
            f"interface {interface_name}",
            "switchport mode access",
            f"switchport access vlan {vlan_id}",
            "exit"
        ]
    elif type == 'trunk':
        commands = [
            f"interface {interface_name}",
            "switchport mode trunk",
            f"switchport trunk allowed vlan add {vlan_id}",
            "exit"
        ]
    else:
        raise ValueError("Invalid interface type. Must be 'access' or 'trunk'.")

    return _run_vlan_command(id, commands)

# Sincronizar puertos con la base de datos
def sync_ports(device_id):
    device = Device.objects.get(id=device_id)  # Obtenemos el dispositivo

    commands = ["do show ip int brief"]
    output = _run_vlan_command(device_id, commands)
    lines = output.splitlines()  # Separamos el output en líneas

    for line in lines[1:]:  # Saltamos el encabezado del show
        parts = line.split()
        if len(parts) < 6:  # Si la línea no tiene todos los campos, la ignoramos
            continue

        name = parts[0]  # Nombre de la interfaz (Ej: Gi0/1)
        ip = parts[1]    # IP asignada (si tiene)
        status = parts[4] == "up"  # True si la interfaz esta activa

        # Crear la interfaz si no existe, o traerla si ya esta creada
        interface, created = Interface.objects.get_or_create(
            device=device,
            name=name,
            defaults={"state": status}
        )

        # Si ya existia, actualizamos el estado
        if not created:
            interface.state = status
            interface.save()
    
    return "Sync completed"  # Regresamos confirmación

def change_port_status_ssh(id, interface_name, status): 
    state = 'shutdown' if status else 'no shutdown'
    commands = [
            f"interface {interface_name}",
            state, 
            "exit"
        ]

    return _run_vlan_command(id, commands)

def refresh_host_for_interface(device, interface):
    time.sleep(4)
    conn = None
    try:
        conn = SSHClient(device.hostname, device.ip_address, device.username, device.password)
        conn.connect()
    except:
        print(f'SSH FAIL {device.hostname}')
        return
    
    # Conseguir la MAC del host
    mac_table = conn.send_command(f'show mac address-table interface {interface.name}')
    mac = parse_mac(mac_table)

    if not mac:
        print(f'No MAC in {interface.name}')
        conn.close()
        return
    
    # Conseguir la IP del host
    arp_table = conn.send_command('show arp')
    ip = find_ip_for_mac(arp_table, mac)

    conn.close()

    # Actualizar/Crear el host en la BD
    Host.objects.update_or_create(
        MAC=mac,
        defaults={
            "ip_host": ip if ip else '0.0.0.0',
            'connected_toInt': interface,
        }
    )
    print(f'[HOST UPDATED] {mac} -> {ip} en {interface.name}')