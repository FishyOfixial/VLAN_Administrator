import socket
from .parser import parse_syslog
from ..models import Device, Interface, SyslogEvent
from django.utils import timezone

def start_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", 514))

    print("Syslog listener iniciado en UDP 514...")

    while True:
        data, addr = sock.recvfrom(4096)
        msg = data.decode(errors="ignore")
        device_ip = addr[0]

        # Guardar en DB y manejar evento
        process_syslog(device_ip, msg)


def process_syslog(device_ip, raw_msg):
    # Verificar si el mensaje pertenece a un dispositivo registrado
    try:
        device = Device.objects.get(ip_address=device_ip)
    except Device.DoesNotExist:
        print('El dispositivo no esta en la BD')
        return  # Se ignora si no es un equipo en la base

    # Parsear mensaje (up/down)
    parsed = parse_syslog(raw_msg)
    if not parsed:
        return

    interface_name = parsed["interface"]
    is_up = parsed["state"]

    # Guardar syslog en la tabla
    SyslogEvent.objects.create(
        device=device,
        timestamp=timezone.now(),
        message=raw_msg,
        severity=5
    )

    # Actualizar estado del puerto
    try:
        interface = Interface.objects.get(device=device, name=interface_name)
        interface.state = is_up
        interface.save()
    except Interface.DoesNotExist:
        pass
