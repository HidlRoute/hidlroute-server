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

"""
For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
from typing import Dict, Any
from django.utils.translation import gettext_lazy as _
from .helper import *
from .base import *

DEBUG_TOOLBAR = env.bool("DEBUG_TOOLBAR", False)
BRUTE_FORCE_PROTECTION = env.bool("BRUTE_FORCE_PROTECTION", True)

# Application definition
INSTALLED_APPS = filter_none(
    [
        "hidlroute.web.apps.WebConfig",
        "jazzmin",
        "hidlroute.apps.HidlAdminConfig",
        "crispy_forms",
        "treebeard",
        "adminsortable2",
        "debug_toolbar" if DEBUG_TOOLBAR else None,
        "defender" if BRUTE_FORCE_PROTECTION else None,
    ]
    + BASE_APPS
    + ["social_django"]
)

INTERNAL_IPS = [
    "127.0.0.1",
]

MIDDLEWARE = filter_none(
    [
        "django.middleware.security.SecurityMiddleware",
        "whitenoise.middleware.WhiteNoiseMiddleware" if not DEBUG else None,
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.locale.LocaleMiddleware",
        "django.middleware.common.CommonMiddleware",
        "debug_toolbar.middleware.DebugToolbarMiddleware" if DEBUG_TOOLBAR else None,
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django_otp.middleware.OTPMiddleware",
        "hidlroute.core.midleware.PreventBruteforceOnLoginMiddleware" if BRUTE_FORCE_PROTECTION else None,
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
        "easyaudit.middleware.easyaudit.EasyAuditMiddleware",
        "two_factor.middleware.threadlocals.ThreadLocals",
    ]
)

ROOT_URLCONF = "hidlroute.urls"

LOGIN_URL = "two_factor:login"
LOGIN_REDIRECT_URL = "two_factor:profile"

# 2FA
TWO_FACTOR_FORCE = env.bool("TWO_FACTOR_FORCE", False)
TWO_FACTOR_PATCH_ADMIN = True
TWO_FACTOR_REMEMBER_COOKIE_PREFIX = "rmb_2fa_"
TWO_FACTOR_REMEMBER_COOKIE_AGE = 3 * 24 * 3600
TWO_FACTOR_REMEMBER_COOKIE_SECURE = True
TWO_FACTOR_REMEMBER_COOKIE_SAMESITE = "Strict"

# Brute force prevention (by django-defender)
# See config docs here: https://django-defender.readthedocs.io/en/latest/#customizing-django-defender
DEFENDER_LOGIN_FAILURE_LIMIT = env.int("DEFENDER_LOGIN_FAILURE_LIMIT", 5)
DEFENDER_COOLOFF_TIME = env.int("DEFENDER_COOLOFF_TIME", 300)
DEFENDER_BEHIND_REVERSE_PROXY = env.bool("BEHIND_PROXY", False)
DEFENDER_REDIS_URL = env.str("DEFENDER_REDIS_URL", None)
DEFENDER_STORE_ACCESS_ATTEMPTS = False
DEFENDER_LOCKOUT_TEMPLATE = "defender/lockout.html"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
                "hidlroute.core.context_processors.admin_menu",
            ],
        },
    },
]

CRISPY_TEMPLATE_PACK = "bootstrap4"
WSGI_APPLICATION = "hidlroute.wsgi.application"

JAZZMIN_SETTINGS: Dict[str, Any] = {
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": env.str("WL_SITE_TITLE", "Hidl Route"),
    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": env.str("WL_SITE_HEADER", env.str("WL_SITE_TITLE", "Hidl Route")),
    # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_brand": env.str("WL_SITE_BRAND", env.str("WL_SITE_TITLE", "Hidl Route")),
    # Logo to use for your site, must be present in static files, used for brand on top left
    "site_logo": env.str("WL_SITE_LOGO", "hidlroute/img/logo-color-hor-small.svg"),
    # Logo to use for your site, must be present in static files, used for login form logo (defaults to site_logo)
    "login_logo": env.str("WL_LOGIN_LOGO", "hidlroute/img/logo-color-white-mid.png"),
    # Logo to use for login form in dark themes (defaults to login_logo)
    "login_logo_dark": None,
    # CSS classes that are applied to the logo above
    "site_logo_classes": env.str("WL_SITE_LOGO_CLASS", ""),
    # Relative path to a favicon for your site, will default to site_logo if absent (ideally 32x32 px)
    "site_icon": env.str("WL_FAVICON", "hidlroute/img/favicon-32.png"),
    # Welcome text on the login screen
    "welcome_sign": env.str("WL_WELCOME_MSG", ""),
    "copyright": "HidlRoute",
    # The model admin to search from the search bar, search bar omitted if excluded
    "search_model": AUTH_USER_MODEL,
    # Field name on user model that contains avatar ImageField/URLField/Charfield or a callable that receives the user
    "user_avatar": "profile_picture",
    # List of apps (and/or models) to base side menu ordering off of (does not need to contain all apps/models)
    "order_with_respect_to": [
        "hidl_auth",
        "hidl_vpn",
        "hidl_core",
        "easyaudit",
    ],
    # Hide these apps when generating side menu e.g (auth)
    "hide_apps": [
        "django_otp",
        "two_factor",
        "otp_static",
        "otp_totp",
        "social_django",
        "defender",
    ],
    # Hide these models when generating side menu (e.g auth.user)
    "hide_models": [
        "hidl_vpn.vpnfirewallrule",
        "hidl_vpn.serverroutingrule",
        # "easyaudit.requestevent", "easyaudit.loginevent", "easyaudit.crudevent"
    ],
    "icons": {
        "auth": "fas fa-users-cog",
        AUTH_USER_MODEL: "fas fa-user",
        "hidl_auth.role": "fas fa-user-tag",
        "easyaudit.requestevent": "fas fa-exchange-alt",
        "easyaudit.loginevent": "fas fa-signature",
        "easyaudit.crudevent": "fas fa-file",
        "hidl_vpn.device": "fas fa-mobile-alt",
        "hidl_vpn.vpnserver": "fas fa-server",
        "hidl_core.host": "fas fa-desktop",
        "hidl_core.group": "fas fa-users",
        "hidl_core.subnet": "fas fa-network-wired",
        "hidl_core.firewallservice": "fas fa-fire",
    },
    # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    #################
    # Related Modal #
    #################
    # Activate Bootstrap modal
    "related_modal_active": True,
    #############
    # User Menu #
    #############
    # Additional links to include in the user menu on the top right ("app" url type is not allowed)
    "usermenu_links": [
        {
            "name": _("Two-Factor Authentication"),
            "url": "two_factor:profile",
            "icon": "fas fa-mobile-alt",
        },
    ],
    "custom_links": {
        "easyaudit": [
            {
                "name": _("Blocked Users"),
                "url": "defender:blocks",
                "icon": "fas fa-user-slash",
                "permissions": ["hidl_auth.can_manage_defender"],
            },
        ],
        "hidl_core": [
            {
                "name": _("Self-service"),
                "url": "selfservice:devices_list",
                "icon": "fas fa-laptop",
                "permissions": ["hidl_vpn.can_manage_own_devices"],
            },
        ],
    },
    #############
    # UI Tweaks #
    #############
    # Relative paths to custom CSS/JS scripts (must be present in static files)
    "custom_css": env.str("WL_CUSTOM_CSS", None),
    "custom_js": env.str("WL_CUSTOM_JS", None),
    # Whether to show the UI customizer on the sidebar
    "show_ui_builder": False,
    ###############
    # Change view #
    ###############
    # Render out the change view as a single form, or in tabs, current options are
    # - single, horizontal_tabs (default), vertical_tabs, collapsible, carousel
    "changeform_format": "horizontal_tabs",
    # override change forms on a per modeladmin basis
    "changeform_format_overrides": {
        "hidl_vpn.vpnfirewallrule": "single",
        "hidl_vpn.serverroutingrule": "single",
        "hidl_core.firewallservice": "single",
    },
    # Add a language dropdown into the admin
    "language_chooser": True,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": False,
    "accent": "accent-primary",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": "darkly",
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-outline-info",
        "warning": "btn-outline-warning",
        "danger": "btn-outline-danger",
        "success": "btn-outline-success",
    },
    "actions_sticky_top": True,
}
