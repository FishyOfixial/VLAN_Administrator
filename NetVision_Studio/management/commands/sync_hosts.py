from django.core.management.base import BaseCommand
from concurrent.futures import ThreadPoolExecutor
from ...networking import refresh_host_for_interface
from ...models import Device, Interface, Vlan
from ...ssh_client import SSHClient


class Command(BaseCommand):
    help = "Sincroniza MAC/IP y fuerza ARP usando VLANs de la BD"

    def handle(self, *args, **kwargs):

        interfaces = Interface.objects.select_related("device").filter(device__device_type='switch')
        vlans = Vlan.objects.values_list("vlan_id", flat=True)
        switches = Device.objects.filter(device_type="switch")

        # --- 1) Forzar ARP broadcast por VLAN en cada switch ---
        def force_arp(device):
            try:
                client = SSHClient(
                    hostname=device.hostname,
                    ip=device.ip_address,
                    username=device.username,
                    password=device.password
                )
                client.connect()

                for vlan_id in vlans:
                    # Generar broadcast para esa VLAN
                    broadcast = f"10.{vlan_id}.0.255"

                    # Ping broadcast para forzar ARP
                    client.run(f"ping {broadcast} repeat 2")

                client.close()

            except Exception as e:
                print(f"[ERROR] ARP broadcast en {device.hostname}: {e}")

        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(force_arp, switches)

        self.stdout.write(self.style.SUCCESS("✓ ARP broadcast enviado para TODAS las VLAN"))


        # --- 2) Refrescar interfaces en paralelo ---
        def process_interface(intf):
            refresh_host_for_interface(intf.device, intf)

        with ThreadPoolExecutor(max_workers=30) as executor:
            executor.map(process_interface, interfaces)

        self.stdout.write(self.style.SUCCESS("✓ Interfaces sincronizadas"))
