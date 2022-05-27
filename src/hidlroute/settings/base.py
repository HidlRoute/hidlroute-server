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

from django.utils.translation import gettext_lazy as _
from .helper import *

DEBUG = env.bool("DEBUG", False)

BASE_APPS = filter_none(
    [
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        # 3rd party
        "hidlroute.web.apps.EasyAuditApp",
        "django_otp",
        "django_otp.plugins.otp_static",
        "django_otp.plugins.otp_totp",
        "two_factor",
        "polymorphic",
        # HidlRoute
        "hidlroute.auth",
        "hidlroute.core",
        if_env_set("hidlroute.worker", "HIDL_WORKERS", False),
        "hidlroute.vpn",
        if_env_set("hidlroute.contrib.wireguard", "ENABLE_WIREGUARD", True),
        if_env_set("hidlroute.contrib.openvpn", "ENABLE_OPENVPN", True),
        if_env_set("hidlroute.contrib.dummy", "ENABLE_DUMMY", False),
    ]
)

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/
LANGUAGES = [
    ("en", _("English")),
    ("uk", _("Ukrainian")),
]
LANGUAGE_CODE = "en-us"
TIME_ZONE = env.str("TIME_ZONE", "UTC")
CELERY_TIMEZONE = TIME_ZONE
USE_I18N = True
USE_L10N = True
LOCALE_DIRS = BASE_DIR / "locale"
USE_TZ = True
FIXTURE_DIRS = [BASE_DIR / "demo-data"]
# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static-files"
if not DEBUG:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Email
if env.str("EMAIL_URL", None) is not None:
    EMAIL_CONFIG = env.email_url("EMAIL_URL")
    vars().update(EMAIL_CONFIG)

# Supported backends:
# https://python-social-auth.readthedocs.io/en/latest/backends/index.html#supported-backends
AUTHENTICATION_BACKENDS = filter_none(
    [
        "social_core.backends.google.GoogleOAuth2",
        "django.contrib.auth.backends.ModelBackend",
    ]
)
AUTH_USER_MODEL = "hidl_auth.User"

SOCIAL_AUTH_JSONFIELD_ENABLED = False
SOCIAL_AUTH_URL_NAMESPACE = "social"

SOCIAL_AUTH_PIPELINE = filter_none(
    [
        "social_core.pipeline.social_auth.social_details",
        "social_core.pipeline.social_auth.social_uid",
        "social_core.pipeline.social_auth.social_user",
        "social_core.pipeline.user.get_username",
        if_env_set("social_core.pipeline.social_auth.associate_by_email", "SOCIAL_ASSOCIATE_EXISTING_USERS", True),
        "social_core.pipeline.user.create_user",
        "social_core.pipeline.social_auth.associate_user",
        "social_core.pipeline.social_auth.load_extra_data",
        "social_core.pipeline.user.user_details",
    ]
)

SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ["username", "first_name", "last_name", "email"]

# Audit
DJANGO_EASY_AUDIT_READONLY_EVENTS = True
DJANGO_EASY_AUDIT_UNREGISTERED_URLS_DEFAULT = [r"^/static/", r"^/favicon.ico$"]
DJANGO_EASY_AUDIT_UNREGISTERED_CLASSES_EXTRA = ["otp_static.StaticToken", "otp_static.StaticDevice"]

# Logger
DEFAULT_LOGGING_LEVEL = "INFO" if not env.bool("DEBUG", False) else "DEBUG"
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "formatters": {
        "verbose": {
            "format": "{name} {levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "standard": {
            "format": "[{levelname}] {asctime} | {name} : {message}",
            "style": "{",
        },
        "simple": {
            "format": "[{levelname}] {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": DEFAULT_LOGGING_LEVEL,
            "propagate": True,
        },
        "root": {
            "level": DEFAULT_LOGGING_LEVEL,
            "handlers": ["console"],
        },
        "two_factor": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "": {
            "level": DEFAULT_LOGGING_LEVEL,
            "handlers": ["console"],
        },
    },
}

CELERY_BEAT_SCHEDULE = {}
