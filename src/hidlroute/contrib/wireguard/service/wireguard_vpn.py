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

from pr2modules.iproute import IPRoute

from hidlroute.contrib.wireguard.models import WireguardServer
from hidlroute.core import models
from hidlroute.core.service.base import VPNService, VPNServerStatus


class WireguardVPNService(VPNService):
    def start(self, server: "models.Server"):
        pass

    def stop(self, server: "models.Server"):
        pass

    def get_status(self, server: models.Server) -> VPNServerStatus:
        if not isinstance(server, WireguardServer):
            raise ValueError("Wireguard VPN Service can only take Wireguard server as an argument.")

        with IPRoute() as ipr:
            link_index = ipr.link_lookup(ifname=server.interface_name)
            if not len(link_index):
                return VPNServerStatus.STOPPED

            link_detail = ipr.get_links(link_index)[0]
            return VPNServerStatus.RUNNING if link_detail.get("state", "down") == "up" else VPNServerStatus.STOPPED
