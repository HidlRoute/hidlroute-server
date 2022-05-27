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
from typing import List

from hidlroute.vpn import models as vpn_models
from hidlroute.core.service.firewall.base import FirewallService
from hidlroute.core.service.networking.base import (
    NetworkingService,
    NetInterface,
    NetInterfaceState,
    InterfaceKind,
    Route,
)
from hidlroute.core.types import IpAddress

LOGGER = logging.getLogger("hidl.contrib.dummy.net")


class DummyFirewallService(FirewallService):
    def __init__(self) -> None:
        super().__init__()
        self.__logger = LOGGER.getChild(".firewall")

    def _log_rule(self, rule: vpn_models.VpnFirewallRule):
        self.__logger.info(rule.repr)

    def setup_firewall_for_server(self, server: vpn_models.VpnServer):
        self.__logger.info("Setup Firewall for {}".format(server))
        self.__logger.info("Adding rules: ")
        for rule in server.get_firewall_rules():
            self._log_rule(rule)
        self.__logger.info("Finished firewall configuration for {}".format(server))

    def destroy_firewall_for_server(self, server: vpn_models.VpnServer):
        self.__logger.info("Destroy Firewall for {}".format(server))
        self.__logger.info("Deleting rules: ")

        for rule in server.get_firewall_rules():
            self._log_rule(rule)
        self.__logger.info("Finished firewall tear down for {}".format(server))


class DummyNetworkingService(NetworkingService):
    def create_route(self, route: Route) -> Route:
        return route

    def delete_route(self, route: Route):
        pass

    def get_routes(self) -> List[Route]:
        return []

    def get_default_routes(self) -> List[Route]:
        return []

    def get_interfaces(self) -> List[NetInterface]:
        return []

    def create_interface(self, ifname: str, kind: InterfaceKind) -> NetInterface:
        interface = NetInterface(ifname, index=999, state=NetInterfaceState.UP, mac_address="00:00:00:00:00")
        self.__logger.info("Created interface: " + str(interface))
        return interface

    def delete_interface(self, ifname: str) -> None:
        self.__logger.info("Deleted interface: " + ifname)

    def add_ip_address(self, interface: NetInterface, address: IpAddress) -> None:
        interface.ip4address = address
        self.__logger.info(f"Added IP address {address} to interface {interface.name}: " + str(interface))

    def set_link_status(self, interface: NetInterface, status: NetInterfaceState) -> None:
        interface.state = status
        self.__logger.info(f"Set state {status} to interface {interface.name}: " + str(interface))

    def __init__(self) -> None:
        super().__init__()
        self.__logger = LOGGER.getChild(".firewall")

    def _log_rule(self, rule: vpn_models.ServerRoutingRule, server: vpn_models.VpnServer):
        self.__logger.info(
            f"\t {rule.network.cidr} gw: {rule.gateway or 'n/a'} "
            f"iface: {rule.resolved_interface_name(server) or 'n/a'}"
        )
