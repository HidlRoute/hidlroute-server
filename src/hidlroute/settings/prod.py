#    Hidl Route - opensource vpn management system
#    Copyright (C) 2023 Dmitry Berezovsky, Alexander Cherednichenko
#
#    Hidl Route is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Hidl Route is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from .base_server import *
from email.utils import getaddresses

SECRET_KEY = env.str("SECRET_KEY")
DEBUG = env.bool("DEBUG")
ALLOWED_HOSTS = env.tuple("ALLOWED_HOSTS")
SERVER_EMAIL = env.str("SERVER_EMAIL", "webmaster@yoursite.org")
X_FRAME_OPTIONS = "ALLOW-FROM " + " ".join(ALLOWED_HOSTS)

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
DATABASES = {"default": env.db_url()}
if "postgresql" in DATABASES["default"]["ENGINE"]:
    SOCIAL_AUTH_JSONFIELD_ENABLED = True

ADMINS = getaddresses([env("ADMINS")])

CELERY_BROKER_URL = env.str("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = env.str("CELERY_RESULT_BACKEND", CELERY_BROKER_URL)

LOGGING["loggers"]["hidl_core.factory"] = {"level": "ERROR"}

try:
    from hidlroute.settings_override import *  # noqa: F401
except ImportError:
    pass
