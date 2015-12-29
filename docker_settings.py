import os

from django.utils.crypto import get_random_string

from homelab.settings import BASE_DIR

chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
if os.environ.get('HOMELAB_SECRET_KEY', '') == '':
    os.environ['HOMELAB_SECRET_KEY'] = get_random_string(50, chars)
SECRET_KEY = os.environ.get('HOMELAB_SECRET_KEY', '')

DEBUG = False

ALLOWED_HOSTS = [os.environ.get('HOMELAB_ALLOWED_HOST', '*')]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('HOMELAB_DB_NAME', 'homelab'),
        'USER': os.environ.get('HOMELAB_DB_USER', ''),
        'PASSWORD': os.environ.get('HOMELAB_DB_PASSWORD', ''),
        # Si non renseigné on prend par défaut le host du container postgres linké sous le nom db
        'HOST': os.environ.get('HOMELAB_DB_HOST', 'db'),
        'PORT': os.environ.get('HOMELAB_DB_PORT', '5432')
    }
}

EMAIL_USE_TLS = os.environ.get('HOMELAB_EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST = os.environ.get('HOMELAB_EMAIL_HOST', 'localhost')
EMAIL_PORT = os.environ.get('HOMELAB_EMAIL_PORT', '587')
EMAIL_HOST_USER = os.environ.get('HOMELAB_EMAIL_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('HOMELAB_EMAIL_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('HOMELAB_EMAIL_DEFAULT_FROM', 'homelab@localhost')
