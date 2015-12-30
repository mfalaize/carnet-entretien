#!/bin/bash
# Systématiquement on met à jour les fichiers statiques et la structure de la base de données
python manage.py collectstatic --noinput
python manage.py migrate auth
python manage.py migrate

case "$1" in
    init)
        # A faire uniquement lors du premier run du container
        python manage.py loaddata initial
        # On créé un superuser pour avoir accès à l'application d'administration django
        echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@localhost', 's3cr3t')" | python manage.py shell
        ;;
esac

apachectl -DFOREGROUND