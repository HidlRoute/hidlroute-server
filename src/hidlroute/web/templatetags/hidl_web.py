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

from typing import List, Dict, Optional, Union, Callable

from django.contrib.auth.models import AbstractUser
from django.template import Library
from django.templatetags.static import static
import jazzmin.settings

from hidlroute.vpn import models as models_vpn

register = Library()


@register.filter
def filter_child_models(apps: List[Dict]) -> List[Dict]:
    target = (models_vpn.VpnServer, models_vpn.Device)
    for app in apps:
        app["models"] = list(
            filter(
                lambda x: not ("model" in x and issubclass(x["model"], target) and x["model"] not in target),
                app["models"],
            )
        )
    return list(filter(lambda x: len(x["models"]) > 0, apps))


@register.inclusion_tag("tags/current_servers.html", takes_context=True)
def current_servers(context):
    request = context["request"]
    return {"servers": models_vpn.VpnServer.get_servers_for_user(request.user)}


@register.simple_tag
def get_hidl_user_avatar(user: AbstractUser):
    """
    For the given user, try to get the avatar image, which can be one of:

        - ImageField on the user model
        - URLField/Charfield on the model
        - A callable that receives the user instance e.g lambda u: u.profile.image.url
    """
    no_avatar = static("vendor/adminlte/img/user2-160x160.jpg")
    options = jazzmin.settings.get_settings()
    avatar_field_name: Optional[Union[str, Callable]] = options.get("user_avatar")

    if not avatar_field_name:
        return no_avatar

    if callable(avatar_field_name):
        return avatar_field_name(user)

    # If we find the property directly on the user model (imagefield or URLfield)
    avatar_field = getattr(user, avatar_field_name, None)
    if avatar_field:
        if type(avatar_field) == str:
            return avatar_field
        elif hasattr(avatar_field, "url"):
            return avatar_field.url
        elif callable(avatar_field):
            return avatar_field(user)

    return no_avatar
