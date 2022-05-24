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

import ipaddress
import time
from typing import Any

DEFAULT_WAIT_SEC = 2


def wait(duration=DEFAULT_WAIT_SEC):
    time.sleep(duration)


def django_enum(cls):
    """
    This is a special fix for wrong Django enum behavior in templates. Enum classes need to be annotated with this.
    see https://code.djangoproject.com/ticket/27910 which seems to be still broken for us
    """
    cls.do_not_call_in_templates = True
    return cls


def is_ip_address(obj: Any) -> bool:
    if obj is None:
        return False
    try:
        ipaddress.ip_address(obj)
        return True
    except ValueError:
        return False


def is_ip_network(obj: Any) -> bool:
    if obj is None:
        return False
    try:
        ipaddress.ip_network(obj)
        return True
    except ValueError:
        return False
