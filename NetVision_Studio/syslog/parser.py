import re

def parse_syslog(message):
    # Regex para capturar puerto y estado (up/down)
    match = re.search(r'Interface\s+(\S+),.*state to (up|down)', message, re.IGNORECASE)

    if not match:
        return None  # No coincide, ignoramos

    interface = match.group(1)
    state = match.group(2).lower() == "up"

    return {
        "interface": interface,
        "state": state
    }
