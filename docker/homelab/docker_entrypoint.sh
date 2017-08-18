#!/bin/sh
set -e

# Systématiquement on met à jour les fichiers statiques et la structure de la base de données
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py init_database

chown -R www-data:www-data data/

apachectl -DFOREGROUND