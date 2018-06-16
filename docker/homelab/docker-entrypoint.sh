#!/bin/sh
set -e

if [ "$1" = 'apachectl' ]; then
    # Systématiquement au démarrage du serveur on met à jour les fichiers statiques et la structure de la base de données
    python manage.py collectstatic --noinput
    python manage.py migrate
    python manage.py init_database
fi

chown -R www-data:www-data data/

# Activation du service de cron si non actif
service cron status || service cron start

exec "$@"
