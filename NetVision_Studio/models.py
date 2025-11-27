from django.db import models

class Device(models.Model):
    DEVICE_TYPES = (
        ("switch", "Switch"),
        ("multilayer", "Multilayer"),
    )

    hostname = models.CharField(max_length=100, unique=True)
    ip_address = models.GenericIPAddressField(protocol='IPv4', unique=True)
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPES, default='switch')

    def __str__(self):
        return f"{self.hostname} ({self.ip_address})"


class Interface(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='interfaces')
    name = models.CharField(max_length=20)
    state = models.BooleanField(default=False)  # True = up
    is_access = models.BooleanField(default=True)
    native = models.PositiveIntegerField(default=1)
    allowed_vlan = models.CharField(max_length=200, blank=True, null=True)  # ejemplo: "10,20,30-40"

    class Meta: # No puedes tener 2 interfaces (fa0/0) en el mismo dispositivo
        unique_together = ('device', 'name')

    def __str__(self):
        return f"{self.device.hostname}-{self.name}"


class TopologyLink(models.Model):
    device_a = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='link_a')
    interface_a = models.ForeignKey(Interface, on_delete=models.CASCADE, related_name='int_a')
    device_b = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='link_b')
    interface_b = models.ForeignKey(Interface, on_delete=models.CASCADE, related_name='int_b')

    def __str__(self):
        return f"{self.device_a.hostname}:{self.interface_a.name} <--> {self.device_b.hostname}:{self.interface_b.name}"


class Vlan(models.Model):
    vlan_id = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"VLAN {self.vlan_id} - {self.name}"



class Vlan_IntAssignment(models.Model):
    interface = models.ForeignKey(Interface, on_delete=models.CASCADE, related_name='vlan_assignment')
    vlan = models.ForeignKey(Vlan, on_delete=models.CASCADE)
    is_native = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.interface} -> VLAN {self.vlan.vlan_id} (Native={self.is_native})"


class SyslogEvent(models.Model):
    device = models.ForeignKey(Device, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField()
    message = models.TextField()
    severity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.timestamp} - {self.device} - Sev {self.severity}"


class Host(models.Model):
    MAC = models.CharField(max_length=17, unique=True)
    ip_host = models.GenericIPAddressField(protocol='IPv4')
    connected_toInt = models.ForeignKey(Interface, on_delete=models.SET_NULL, null=True)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.MAC} ({self.ip_host})"


class ConfLog(models.Model):
    interface = models.ForeignKey(Interface, on_delete=models.CASCADE)
    prev_mode = models.CharField(max_length=20)   # access / trunk
    new_mode = models.CharField(max_length=20)
    prev_native = models.PositiveIntegerField()
    new_native = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.timestamp}] {self.interface} mode {self.prev_mode} → {self.new_mode}"
