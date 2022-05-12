from .base_server import *

SECRET_KEY = "django-insecure-56=tojj)c&&vurqvd=afvhqzxc095cub@hxf7dd$^iqpm=h$_k"
DEBUG = True
ALLOWED_HOSTS = ["*"]

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR.parent / "dev-data" / "db.sqlite3",
    }
}

# Email
EMAIL_CONFIG = env.email_url_config('smtp://user:password@localhost:1025')
vars().update(EMAIL_CONFIG)
