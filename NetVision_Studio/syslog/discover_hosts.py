from ..models import Host
import time
from .utils import *

def handle_port_up(device, interface):
    # Esperar a que el host recupere DHCP
    time.sleep(5)

    conn = connect_to_device(device)

    # 1. Sacar MAC del puerto
    mac_output = conn.send_command(
        f"show mac address-table interface {interface.name}"
    )
    mac = parse_mac(mac_output)

    if not mac:
        print("No MAC encontrada todavía")
        return

    # 2. Sacar IP usando ARP
    arp_output = conn.send_command("show arp")
    ip = find_ip_for_mac(arp_output, mac)

    # 3. Guardar en la base de datos
    Host.objects.update_or_create(
        MAC=mac,
        defaults={
            "ip_host": ip if ip else "0.0.0.0",
            "connected_toInt": interface
        }
    )

    print(f"Host actualizado: MAC {mac} → IP {ip}")
