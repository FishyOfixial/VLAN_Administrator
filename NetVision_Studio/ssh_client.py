from netmiko import ConnectHandler
from django.conf import settings

# Manejo de errores personalizado
class SSHConnectionError(Exception):
    pass

# Clase para conectar con cada dispositivo y envio de comandos
class SSHClient:

    # Info para la conexion con el dispositivo
    def __init__(self, hostname, ip, username, password, device_type='cisco_ios'):
        self.device = {
            "device_type": device_type,
            "host": ip,
            "username": username,
            "password": password,
            "secret": password,
        }
        self.hostname = hostname
        self.connection = None
    
    # Metodo para conectarnos al dispositivo
    def connect(self):
        try:
            self.connection = ConnectHandler(**self.device)
            self.connection.enable()
        except Exception as e:
            raise SSHConnectionError(f'No se pudo conectar a {self.hostname}: {str(e)}')
    
    # Metodo para enviar un solo comando
    def send_command(self, cmd):
        if not self.connection:
            raise SSHConnectionError('No hay conexion activa')
        return self.connection.send_command(cmd)
    
    # Metodo para enviar una lista de comandos
    def send_config(self, commands):
        if not self.connection:
            raise SSHConnectionError('No hay conexion activa')
        return self.connection.send_config_set(commands)
    
    # Metodo para cerrar la conexion
    def close(self):
        if self.connection:
            self.connection.disconnect()
            self.connection = None