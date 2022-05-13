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

from django.contrib.auth import signals, get_user_model
from django.db import transaction
from django.utils.module_loading import import_string

from easyaudit.middleware.easyaudit import get_current_request
from easyaudit.models import LoginEvent
from easyaudit.settings import REMOTE_ADDR_HEADER, WATCH_AUTH_EVENTS, LOGGING_BACKEND

audit_logger = import_string(LOGGING_BACKEND)()


def user_logged_in(sender, request, user, **kwargs):
    try:
        with transaction.atomic():
            login_event = audit_logger.login({
                'login_type': LoginEvent.LOGIN,
                'username': getattr(user, user.USERNAME_FIELD),
                'user_id': getattr(user, 'id', None),
                'remote_ip': request.META[REMOTE_ADDR_HEADER]
            })
    except:
        pass


def user_logged_out(sender, request, user, **kwargs):
    try:
        with transaction.atomic():
            login_event = audit_logger.login({
                'login_type': LoginEvent.LOGOUT,
                'username': getattr(user, user.USERNAME_FIELD),
                'user_id': getattr(user, 'id', None),
                'remote_ip': request.META[REMOTE_ADDR_HEADER]
            })
    except:
        pass


def user_login_failed(sender, credentials, **kwargs):
    try:
        with transaction.atomic():
            request = get_current_request() # request argument not available in django < 1.11
            user_model = get_user_model()
            login_event = audit_logger.login({
                'login_type': LoginEvent.FAILED,
                'username': credentials[user_model.USERNAME_FIELD],
                'remote_ip': request.META[REMOTE_ADDR_HEADER]
            })
    except:
        pass


if WATCH_AUTH_EVENTS:
    signals.user_logged_in.connect(user_logged_in, dispatch_uid='easy_audit_signals_logged_in')
    signals.user_logged_out.connect(user_logged_out, dispatch_uid='easy_audit_signals_logged_out')
    signals.user_login_failed.connect(user_login_failed, dispatch_uid='easy_audit_signals_login_failed')
