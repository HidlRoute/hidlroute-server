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

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from hidlroute.contrib.wireguard import models
from hidlroute.core import models as core_models
from hidlroute.core.admin import ServerAdmin, DeviceAdmin


class ServerInlineAdmin(admin.TabularInline):
    model = core_models.Server


@DeviceAdmin.register_implementation()
class WireguardPeerAdmin(admin.ModelAdmin):
    base_model = models.WireguardPeer
    verbose_name = _("Wireguard Peer")


@ServerAdmin.register_implementation()
class WireguardServerAdmin(ServerAdmin.Impl):
    ICON = "images/server/wireguard.png"

    base_model = models.WireguardServer
    verbose_name = _("Wireguard Config")
    verbose_name_plural = verbose_name
    fieldsets = ServerAdmin.Impl.fieldsets + [(_("Wireguard"), {"fields": ["listen_port", "private_key"]})]
