from django.contrib.auth.models import User
from django.core.management import execute_from_command_line


if User.objects.count() == 0:
    execute_from_command_line(["manage.py", "loaddata", "initial"])
    User.objects.create_superuser('admin', 'admin@localhost', 's3cr3t')
