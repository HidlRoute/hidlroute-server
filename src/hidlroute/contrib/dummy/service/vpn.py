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

import logging
from typing import TYPE_CHECKING

from django.utils.functional import cached_property
from django.views.generic import TemplateView

from hidlroute.vpn.service.base import ServerState, ServerStatus, VPNService, VPNServiceViews
from hidlroute.vpn.views import BaseVPNDeviceConfigView

if TYPE_CHECKING:
    from hidlroute.vpn import models as vpn_models

LOGGER = logging.getLogger("hidl.contrib.dummy")


class DummyVPNConfigView(TemplateView, BaseVPNDeviceConfigView):
    def __init__(self, *args, **kwargs):
        super().__init__(template_name="hidl_dummy/config_view.html", *args, **kwargs)

    def post(self, request, device):
        return self.get(request, device=device)


class DummyVPNViews(VPNServiceViews):
    @cached_property
    def vpn_details_view(self):
        return DummyVPNConfigView.as_view()


class DummyLoggingVPNService(VPNService):
    def __init__(self) -> None:
        super().__init__()
        self.__logger = LOGGER.getChild(".vpn")

    def _log_routing_rule(self, rule: "vpn_models.ServerRoutingRule", server: "vpn_models.VpnServer"):
        self.__logger.info(
            f"\t {rule.network.cidr} gw: {rule.gateway or 'n/a'} "
            f"iface: {rule.resolved_interface_name(server) or 'n/a'}"
        )

    def _log_firewall_rule(self, rule: "vpn_models.VpnFirewallRule"):
        self.__logger.info(rule.repr)

    def do_vpn_server_start(self, server: "vpn_models.VpnServer"):
        LOGGER.info(f"Setting up VPN server: {server}")
        LOGGER.info(f"Creating network interface {server.interface_name}")
        server.service_factory.networking_service.setup_routes_for_server(server)
        server.service_factory.firewall_service.setup_firewall_for_server(server)
        LOGGER.info(f"VPN Server {server} is up and running")

    def setup_routes_for_server(self, server: "vpn_models.VpnServer"):
        self.__logger.info("Setup Routes for {}".format(server))
        self.__logger.info("Adding routes: ")
        for rule in server.get_routing_rules():
            self._log_routing_rule(rule, server)
        self.__logger.info("Finished routes configuration for {}".format(server))

    def destroy_routes_for_server(self, server: "vpn_models.VpnServer"):
        self.__logger.info("Destroy Routes for {}".format(server))
        self.__logger.info("Deleting routes: ")
        for rule in server.get_routing_rules():
            self._log_routing_rule(rule, server)
        self.__logger.info("Deleted routes for {}".format(server))

    def do_vpn_server_stop(self, server: "vpn_models.VpnServer"):
        LOGGER.info(f"Shutting down VPN server: {server}")
        LOGGER.info(f"Destroying network interface {server.interface_name}")
        server.service_factory.firewall_service.destroy_firewall_for_server(server)
        server.service_factory.networking_service.destroy_routes_for_server(server)
        LOGGER.info(f"VPN Server {server} is terminated")

    def do_get_status(self, server: "vpn_models.VpnServer") -> ServerStatus:
        LOGGER.info(f"Get server status: {server}")
        return ServerStatus(state=ServerState.STOPPED)

    @cached_property
    def views(self):
        return DummyVPNViews()
