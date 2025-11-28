from .models import Device, Vlan
from .ssh_client import SSHClient

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
def add_vlan(device_id, vlan_id):
    vlan = Vlan.objects.get(vlan_id=vlan_id)

    commands = [
        f"vlan {vlan.vlan_id}",
        f"name {vlan.name}",
        "exit"
    ]

    return _run_vlan_command(device_id, commands)


# Borrar VLAN del dispositivo
def delete_vlan(device_id, vlan_id):
    commands = [
        f"no vlan {vlan_id}",
        "exit"
    ]

    return _run_vlan_command(device_id, commands)
