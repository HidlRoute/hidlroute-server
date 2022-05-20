from pr2modules.iproute import IPRoute

from hidlroute.contrib.wireguard.models import WireguardServer
from hidlroute.core import models
from hidlroute.core.service.base import VPNService, VPNServerStatus


class WireguardVPNService(VPNService):

    def get_status(self, server: models.Server) -> VPNServerStatus:
        if not isinstance(server, WireguardServer):
            raise ValueError("Wireguard VPN Service can only take Wireguard server as an argument.")

        with IPRoute() as ipr:
            link_index = ipr.link_lookup(ifname=server.interface_name)
            if not len(link_index):
                return False

            link_detail = ipr.get_links(link_index)[0]
            return link_detail.get("state", "down") == "up"
