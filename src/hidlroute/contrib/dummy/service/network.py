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

from hidlroute.core import models
from hidlroute.core.service.base import WorkerService, VPNServerStatus, VPNService
from hidlroute.core.service.firewall.base import FirewallService
from hidlroute.core.service.routing.base import RoutingService

LOGGER = logging.Logger("hidle.contrib.dummy.service")


class DummyFirewallService(FirewallService):
    def setup_firewall_for_server(self, server: models.Server):
        LOGGER.info("Setup Firewall for {}".format(server))

    def destroy_firewall_for_server(self, server: models.Server):
        LOGGER.info("Destroy Firewall for {}".format(server))


class DummyRoutingService(RoutingService):
    def setup_routes_for_server(self, server: models.Server):
        LOGGER.info("Setup Routes for {}".format(server))

    def destroy_routes_for_server(self, server: models.Server):
        LOGGER.info("Destroy Routes for {}".format(server))

class DummyLoggingVPNService(VPNService):

    def get_status(self, server: "models.Server") -> VPNServerStatus:
        return VPNServerStatus.STOPPED


class DummySyncrhonousWorkerService(WorkerService):
    def get_server_status(self, server: models.Server) -> VPNServerStatus:
        return server.get_vpn_service().get_status(server)
