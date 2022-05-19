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

from typing import List, Dict

from django.template import Library
from hidlroute.core import models as models_core

register = Library()


@register.filter
def filter_child_models(apps: List[Dict]) -> List[Dict]:
    target = (models_core.Server, models_core.Device)
    for app in apps:
        app["models"] = list(
            filter(lambda x: not (issubclass(x["model"], target) and x["model"] not in target), app["models"])
        )
    return list(filter(lambda x: len(x["models"]) > 0, apps))
