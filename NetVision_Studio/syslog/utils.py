import re
from ..ssh_client import SSHClient

def connect_to_device(device):
    client = SSHClient(
        hostname=device.hostname,
        ip=device.ip_address,
        username=device.username,
        password=device.password
    )
    client.connect()
    return client


def parse_mac(output):
    match = re.search(r'([0-9A-Fa-f]{4}\.[0-9A-Fa-f]{4}\.[0-9A-Fa-f]{4})', output)
    return match.group(1) if match else None


def find_ip_for_mac(arp_output, mac):
    print(arp_output)
    print(mac)
    compact = mac.replace(".", "")
    match = re.search(rf'{compact}.*?(\d+\.\d+\.\d+\.\d+)', arp_output)
    print(match)
    return match.group(1) if match else None
