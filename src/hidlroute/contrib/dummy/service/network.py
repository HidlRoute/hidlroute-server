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

from hidlroute.core import models as core_models
from hidlroute.core.service.firewall.base import FirewallService
from hidlroute.core.service.routing.base import RoutingService

LOGGER = logging.getLogger("hidl.contrib.dummy.net")


class DummyFirewallService(FirewallService):
    def __init__(self) -> None:
        super().__init__()
        self.__logger = LOGGER.getChild(".firewall")

    def _log_rule(self, rule: core_models.FirewallRule):
        self.__logger.info(f"\t {rule.action} From: To: ")

    def setup_firewall_for_server(self, server: core_models.Server):
        self.__logger.info("Setup Firewall for {}".format(server))
        self.__logger.info("Adding rules: ")
        for rule in server.get_firewall_rules():
            self._log_rule(rule)
        self.__logger.info("Finished firewall configuration for {}".format(server))

    def destroy_firewall_for_server(self, server: core_models.Server):
        self.__logger.info("Destroy Firewall for {}".format(server))
        self.__logger.info("Deleting rules: ")

        for rule in server.get_firewall_rules():
            self._log_rule(rule)
        self.__logger.info("Finished firewall tear down for {}".format(server))


class DummyRoutingService(RoutingService):
    def __init__(self) -> None:
        super().__init__()
        self.__logger = LOGGER.getChild(".firewall")

    def _log_rule(self, rule: core_models.ServerRoutingRule, server: core_models.Server):
        self.__logger.info(
            f"\t {rule.network.cidr} gw: {rule.gateway or 'n/a'} "
            f"iface: {rule.resolved_interface_name(server) or 'n/a'}"
        )

    def setup_routes_for_server(self, server: core_models.Server):
        self.__logger.info("Setup Routes for {}".format(server))
        self.__logger.info("Adding routes: ")
        for rule in server.get_routing_rules():
            self._log_rule(rule, server)
        self.__logger.info("Finished routes configuration for {}".format(server))

    def destroy_routes_for_server(self, server: core_models.Server):
        self.__logger.info("Destroy Routes for {}".format(server))
        self.__logger.info("Deleting routes: ")
        for rule in server.get_routing_rules():
            self._log_rule(rule, server)
        self.__logger.info("Deleted routes for {}".format(server))
