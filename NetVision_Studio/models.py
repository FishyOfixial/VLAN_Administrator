from django.db import models

# Create your models here.
class Device(models.Model):
    type = models.CharField(max_length=20, null=False, blank=False)
    ip_device = models.GenericIPAddressField(unique=True)
    hostname = models.CharField(max_length=50, blank=True, null=False, default='Device')

class Interface(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='id_device')
    name = models.CharField(max_length=20, null=False, blank=False)
    state = models.BooleanField(default=False)
    is_access = models.BooleanField(default=True)
    native = models.PositiveIntegerField(default=1, null=False)
    allowed_vlan = models.CharField(max_length=200, blank=True, null=True)

class TopologyLink(models.Model):
    device_a = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='link_a')
    interface_a = models.ForeignKey(Interface, on_delete=models.CASCADE, related_name='int_a')
    device_b = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='link_b')
    interface_b = models.ForeignKey(Interface, on_delete=models.CASCADE, related_name='int_b')

class Vlan(models.Model):
    vlan_id = models.PositiveIntegerField(null=False, blank=False,)
    name = models.CharField(max_length=20, null=False, blank=False)

class Vlan_IntAssignment(models.Model):
    interface = models.ForeignKey(Interface, on_delete=models.CASCADE, related_name='assigned_Interfaces')
    vlan = models.ForeignKey(Vlan, on_delete=models.CASCADE, related_name='assigned_vlan')
    is_Native = models.BooleanField(default=False)

class SyslogEvent(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='device_logs')
    timeStamp = models.DateTimeField(null=False, blank=False)
    message = models.CharField(max_length=150, null=True, blank=True)
    severity = models.PositiveIntegerField(null=False, blank=False)

class Host(models.Model):
    MAC = models.CharField(null=False, blank=True, max_lenght=17 unique=True)
    ip_host = models.GenericIPAddressField(null=False, blank=False) #unique?
    connected_toInt = models.ForeignKey(Interface, on_delete=models.CASCADE, related_name='int_connectedTo')
    first_seen = models.DateTimeField(auto_now_add=True)
    first_seen = models.DateTimeField(auto_now=True)

class ConfLog(models.Model):
    interface = models.ForeignKey(Interface, on_delete=models.CASCADE, related_name='conf_interface')
    prev_mode = models.CharField(null=False, blank=False max_length=20)
    new_mode = models.CharField(null=False, blank=False max_length=20)
    prev_native = models.CharField(null=False, blank=False max_length=20)
    new_native = models.CharField(null=False, blank=False max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)