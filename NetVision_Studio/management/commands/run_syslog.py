from django.core.management.base import BaseCommand
from ...syslog.listener import start_listener

class Command(BaseCommand):
    help = "Inicia el listener Syslog"

    def handle(self, *args, **kwargs):
        start_listener()
