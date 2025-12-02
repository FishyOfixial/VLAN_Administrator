from django.core.management.base import BaseCommand
from ...networking import refresh_host_for_interface
from ...models import Device, Interface

class Command(BaseCommand):
    help = "Sincroniza MAC e IPs"

    def handle(self, *args, **kwargs):
        switches = Device.objects.filter(device_type="switch")
        interfaces = Interface.objects.filter(device__in=switches)

        #for iface in interfaces:
        #    device = iface.device
        #    refresh_host_for_interface(device, iface)
        refresh_host_for_interface(Device.objects.get(pk=4), Interface.objects.get(pk=130))
