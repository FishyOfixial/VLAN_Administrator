import time
from .models import Device, Vlan, Interface, Host, TopologyLink
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

    create_dhcp(vlan_id)
    configure_hsrp(vlan_id)
    #add_vlan_to_trunks(vlan_id)
    return _run_vlan_command(device_id, commands)

def create_dhcp(vlan_id):
    vlan = Vlan.objects.get(vlan_id=vlan_id)
    multilayers = Device.objects.filter(device_type="multilayer")
    
    multilayers = list(multilayers)
    if not multilayers:
        return
    
    network = f"10.{vlan.vlan_id}.0.0"
    mask = "255.255.255.0"
    gateway = f"10.{vlan.vlan_id}.0.1"

    ranges = [
        (1, 127),
        (128, 254)
    ]

    for idx, d in enumerate(multilayers):
        if idx >= 2:
            break

        start, end = ranges[idx]
        commands = [
            # Rango exclusivo por multilayer
            f"ip dhcp excluded-address 10.{vlan.vlan_id}.0.{start} 10.{vlan.vlan_id}.0.{end}",
            # IP virtual/HSPR o última IP siempre excluida
            f"ip dhcp excluded-address 10.{vlan.vlan_id}.0.254",

            # Crear la pool
            f"ip dhcp pool VLAN{vlan.vlan_id}",
            f"network {network} {mask}",
            f"default-router {gateway}",
        ]

        _run_vlan_command(d.pk, commands)

def configure_hsrp(vlan_id):
    vlan = Vlan.objects.get(vlan_id=vlan_id)
    multilayers = list(Device.objects.filter(device_type='multilayer'))

    multilayers.sort(key=lambda d: d.ip_address)
    ml2 = multilayers[0] # Termina en .2
    ml3 = multilayers[1] # Termina en .3

    vip = f"10.{vlan.vlan_id}.0.1"
    ip_ml2 = f"10.{vlan.vlan_id}.0.2"
    ip_ml3 = f"10.{vlan.vlan_id}.0.3"

    vlan_num = int(vlan_id)
    if vlan_num % 2 == 0:
        active = ml3
        standby = ml2
        active_ip = ip_ml3
        standby_ip = ip_ml2
    else:
        active = ml2
        standby = ml3
        active_ip = ip_ml2
        standby_ip = ip_ml3

    ACTIVE_PRIO = 110
    STANDBY_PRIO = 100

    commands_active = [
        f"interface vlan {vlan_id}",
        f" ip address {active_ip} 255.255.255.0",
        f" standby {vlan_id} ip {vip}",
        f" standby {vlan_id} priority {ACTIVE_PRIO}",
        f" standby {vlan_id} preempt",
    ]

    commands_standby = [
        f"interface vlan {vlan_id}",
        f" ip address {standby_ip} 255.255.255.0",
        f" standby {vlan_id} ip {vip}",
        f" standby {vlan_id} priority {STANDBY_PRIO}",
        f" standby {vlan_id} preempt",
    ]

    _run_vlan_command(active.pk, commands_active)
    _run_vlan_command(standby.pk, commands_standby)

def add_vlan_to_trunks(vlan_id):
    vlan = Vlan.objects.get(vlan_id=vlan_id)
    links = TopologyLink.objects.all()

    for link in links:
        intA = link.interface_a
        intB = link.interface_b

        if intA.mode == 'trunk' and intB.mode == 'trunk':
            sshA = SSHClient(hostname=intA.device.hostname,
                            ip=intA.device.ip_address,
                            username=intA.device.username,
                            password=intA.device.password)
            sshA.connect()
            sshA.send_config([
                f"interface {intA.name}",
                f"switchport trunk allowed vlan add {vlan_id}"
            ])
            sshA.close()

            sshB = SSHClient(
                hostname=intB.device.hostname,
                ip=intB.device.ip_address,
                username=intB.device.username,
                password=intB.device.password
            )
            sshB.connect()
            sshB.send_config([
                f"interface {intB.name}",
                f"switchport trunk allowed vlan add {vlan_id}"
            ])
            sshB.close()


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