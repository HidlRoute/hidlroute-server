from .base_server import *
from email.utils import getaddresses

SECRET_KEY = env.str("SECRET_KEY")
DEBUG = env.bool("DEBUG")
ALLOWED_HOSTS = env.tuple("ALLOWED_HOSTS")
SERVER_EMAIL = env.str('SERVER_EMAIL', 'webmaster@yoursite.org')

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
DATABASES = {
    "default": env.db_url()
}

ADMINS = getaddresses([env('ADMINS')])
