from django.contrib.auth.models import User
from django.core.management import BaseCommand, call_command


def init_database():
    call_command("loaddata", "initial")
    if User.objects.count() == 0:
        User.objects.create_superuser('admin', 'admin@localhost', 's3cr3t')


class Command(BaseCommand):
    help = "Initialise la base de données avec des données indispensables"

    def handle(self, *args, **options):
        init_database()
