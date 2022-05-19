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

import os

os.environ.setdefault("DEBUG", "True")
os.environ.setdefault("ENABLE_DUMMY", "True")
from .base_server import *

SECRET_KEY = "django-insecure-56=tojj)c&&vurqvd=afvhqzxc095cub@hxf7dd$^iqpm=h$_k"
DEBUG = True
ALLOWED_HOSTS = ["*"]
X_FRAME_OPTIONS = "ALLOW-FROM " + " ".join(ALLOWED_HOSTS)
AUTH_PASSWORD_VALIDATORS = []

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR.parent / "dev-data" / "db.sqlite3",
#     }
# }


DATABASES = {"default": env.db_url_config("postgres://hidl:hidl@127.0.0.1:5432/hidl")}

# 2FA
TWO_FACTOR_SMS_GATEWAY = "two_factor.gateways.fake.Fake"

# Email
EMAIL_CONFIG = env.email_url_config("smtp://user:password@localhost:1025")
vars().update(EMAIL_CONFIG)
