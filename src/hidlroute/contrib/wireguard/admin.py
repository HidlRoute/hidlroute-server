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

from django.http import FileResponse
from django.utils.translation import gettext_lazy as _

from hidlroute.contrib.wireguard import models
from hidlroute.contrib.wireguard.service.key import generate_private_key
from hidlroute.vpn.admin import DeviceAdmin, ServerAdmin


@DeviceAdmin.register_implementation(models.WireguardPeer)
class WireguardPeerAdmin(DeviceAdmin.Impl):
    base_model = models.WireguardPeer
    verbose_name = _("Wireguard Peer")

    def response_change(self, request, obj: models.WireguardPeer):
        if "generate-config" in request.POST:
            config = obj.get_real_instance().generate_config()
            return FileResponse(config.as_stream(), filename=config.name, as_attachment=True)
        return super().response_change(request, obj)


@ServerAdmin.register_implementation(models.WireguardServer)
class WireguardServerAdmin(ServerAdmin.Impl):
    ICON = "images/server/wireguard.png"
    base_model = models.WireguardServer
    verbose_name = _("Wireguard Config")
    verbose_name_plural = verbose_name
    fieldsets = ServerAdmin.Impl.fieldsets + [
        (
            _("Wireguard"),
            {"fields": ["client_endpoint", "listen_port", "private_key", "client_dns", "client_keep_alive"]},
        )
    ]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is None:  # For create form only
            form.base_fields["private_key"].initial = generate_private_key
            default_client_host: str = request.get_host()
            if ":" in default_client_host:
                default_client_host = default_client_host.split(":")[0].strip()
            form.base_fields["client_endpoint"].initial = default_client_host
        return form
