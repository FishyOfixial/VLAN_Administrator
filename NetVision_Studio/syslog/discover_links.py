from ..models import Device, Interface, TopologyLink
from ..ssh_client import SSHClient  # tu clase que ya tienes


def parse_cdp(output):
    """Parsea CDP detail y retorna un dict local_int -> (remote_host, remote_int)."""
    neighbors = {}
    blocks = output.split("Device ID: ")
    for b in blocks[1:]:
        try:
            remote_host = b.split("\n")[0].strip()
            local_int = b.split("Interface: ")[1].split(",")[0].strip()
            remote_int = b.split("Port ID (outgoing port): ")[1].split("\n")[0].strip()

            neighbors[local_int] = (remote_host, remote_int)
        except:
            continue

    return neighbors


def create_link(device_a, int_a, device_b, int_b):
    """Guarda un enlace CDP evitando duplicados A<->B."""

    dev_a = Device.objects.filter(hostname=device_a).first()
    dev_b = Device.objects.filter(hostname=device_b).first()
    if not dev_a or not dev_b:
        return

    iface_a = Interface.objects.filter(device=dev_a, name=int_a).first()
    iface_b = Interface.objects.filter(device=dev_b, name=int_b).first()
    if not iface_a or not iface_b:
        return

    # Duplicado directo
    if TopologyLink.objects.filter(
        device_a=dev_a, interface_a=iface_a,
        device_b=dev_b, interface_b=iface_b
    ).exists():
        return

    # Duplicado invertido
    if TopologyLink.objects.filter(
        device_a=dev_b, interface_a=iface_b,
        device_b=dev_a, interface_b=iface_a
    ).exists():
        return

    # Crear
    TopologyLink.objects.create(
        device_a=dev_a,
        interface_a=iface_a,
        device_b=dev_b,
        interface_b=iface_b
    )


def sync_links():
    """Descubre vecinos CDP en todos los dispositivos y almacena los links."""

    devices = Device.objects.all()  # multilayer/core

    print("\n=== Descubriendo enlaces CDP ===")

    for device in devices:
        print(f"\nConsultando CDP en {device.hostname} ({device.ip_address})...")

        ssh = SSHClient(
            hostname=device.hostname,
            ip=device.ip_address,
            username=device.username,
            password=device.password,
        )

        try:
            ssh.connect()
        except Exception as e:
            print(f"  ❌ Error SSH: {e}")
            continue

        try:
            output = ssh.send_command("show cdp neighbors detail")
        except Exception as e:
            print(f"  ❌ Error CDP: {e}")
            ssh.close()
            continue

        ssh.close()

        neighbors = parse_cdp(output)

        if not neighbors:
            print("  ⚠ No se encontraron vecinos CDP")
            continue

        # Crear enlaces
        for local_int, (remote_host, remote_int) in neighbors.items():
            print(f"  ➜ {local_int} → {remote_host}:{remote_int}")
            create_link(device.hostname, local_int, remote_host, remote_int)

    print("\n✓ Links sincronizados.\n")
