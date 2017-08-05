#!/bin/bash
# Systématiquement on met à jour les fichiers statiques et la structure de la base de données
python manage.py collectstatic --noinput
python manage.py migrate auth
python manage.py migrate

echo "exec(open('init.py').read())" | python manage.py shell

chown -R www-data:www-data data/

apachectl -DFOREGROUND