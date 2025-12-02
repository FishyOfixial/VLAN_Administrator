from ..models import Device, Interface, Vlan, Vlan_IntAssignment
from ..ssh_client import SSHClient  # tu clase SSH ya existente
import re


def parse_vlan(output):
    """
    Parsea el output de 'show vlan brief' y devuelve un dict:
    {vlan_id: {'name': vlan_name}}
    """
    vlans = {}
    for line in output.splitlines():
        # Línea ejemplo: "10  Marketing       active"
        match = re.match(r"^\s*(\d+)\s+(\S+)", line)
        if match:
            vlan_id = int(match.group(1))
            name = match.group(2)
            vlans[vlan_id] = {'name': name}
    return vlans


def parse_interfaces(output):
    """
    Parsea 'show interfaces switchport' y devuelve un dict:
    {interface_name: {'access_vlan': vlan_id, 'native_vlan': vlan_id}}
    """
    interfaces = {}
    current_int = None
    for line in output.splitlines():
        # Detecta interfaz
        int_match = re.match(r"^(\S+) is .*", line)
        if int_match:
            current_int = int_match.group(1)
            interfaces[current_int] = {'access_vlan': None, 'native_vlan': None}
            continue

        if current_int:
            access_match = re.search(r"Access Mode VLAN:\s+(\d+)", line)
            if access_match:
                interfaces[current_int]['access_vlan'] = int(access_match.group(1))

            native_match = re.search(r"Trunking Native Mode VLAN:\s+(\d+)", line)
            if native_match:
                interfaces[current_int]['native_vlan'] = int(native_match.group(1))
    return interfaces


def sync_vlans():
    """
    Sincroniza la tabla Vlan y las asignaciones de interfaces Vlan_IntAssignment.
    Toma como VTP Server el Device con pk=1.
    """
    vtp_server = Device.objects.filter(pk=1).first()
    if not vtp_server:
        print("❌ No se encontró el VTP Server con pk=1")
        return

    print(f"\n=== Sincronizando VLANs desde {vtp_server.hostname} ===")

    # Conexión SSH al VTP Server
    ssh = SSHClient(
        hostname=vtp_server.hostname,
        ip=vtp_server.ip_address,
        username=vtp_server.username,
        password=vtp_server.password,
    )

    try:
        ssh.connect()
        vlan_output = ssh.send_command("show vlan brief")
        ssh.close()
    except Exception as e:
        print(f"❌ Error SSH al obtener VLANs: {e}")
        return

    vlans = parse_vlan(vlan_output)
    for vlan_id, data in vlans.items():
        vlan_obj, created = Vlan.objects.get_or_create(
            vlan_id=vlan_id,
            defaults={'name': data['name']}
        )
        if not created and vlan_obj.name != data['name']:
            vlan_obj.name = data['name']
            vlan_obj.save()

    print(f"✓ VLANs sincronizadas ({len(vlans)})")

    # Ahora sincronizamos las interfaces de cada switch
    for device in Device.objects.all():
        print(f"\nActualizando interfaces en {device.hostname}...")

        ssh = SSHClient(
            hostname=device.hostname,
            ip=device.ip_address,
            username=device.username,
            password=device.password,
        )
        try:
            ssh.connect()
            int_output = ssh.send_command("show interfaces switchport")
            ssh.close()
        except Exception as e:
            print(f"  ❌ Error SSH: {e}")
            continue

        interfaces = parse_interfaces(int_output)

        for int_name, vlans_data in interfaces.items():
            iface = Interface.objects.filter(device=device, name=int_name).first()
            if not iface:
                continue

            # Asignación de Access VLAN
            if vlans_data['access_vlan']:
                vlan_obj = Vlan.objects.filter(vlan_id=vlans_data['access_vlan']).first()
                if vlan_obj:
                    assignment, _ = Vlan_IntAssignment.objects.update_or_create(
                        interface=iface,
                        vlan=vlan_obj,
                        defaults={'is_native': False}
                    )

            # Asignación de Native VLAN
            if vlans_data['native_vlan']:
                vlan_obj = Vlan.objects.filter(vlan_id=vlans_data['native_vlan']).first()
                if vlan_obj:
                    assignment, _ = Vlan_IntAssignment.objects.update_or_create(
                        interface=iface,
                        vlan=vlan_obj,
                        defaults={'is_native': True}
                    )

    print("\n✓ Sincronización de interfaces VLAN completada.\n")
