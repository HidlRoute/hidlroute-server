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

from hidlroute.core.service.base import VPNService, ServerStateEnum, ServerStatus

if TYPE_CHECKING:
    from hidlroute.core import models as core_models

LOGGER = logging.getLogger("hidl.contrib.dummy.vpn")


class DummyLoggingVPNService(VPNService):
    def start(self, server: "core_models.Server"):
        LOGGER.info(f"Setting up VPN server: {server}")
        LOGGER.info(f"Creating network interface {server.interface_name}")
        server.service_factory.networking_service.setup_routes_for_server(server)
        server.service_factory.firewall_service.setup_firewall_for_server(server)
        LOGGER.info(f"VPN Server {server} is up and running")

    def stop(self, server: "core_models.Server"):
        LOGGER.info(f"Shutting down VPN server: {server}")
        LOGGER.info(f"Destroying network interface {server.interface_name}")
        server.service_factory.firewall_service.destroy_firewall_for_server(server)
        server.service_factory.networking_service.destroy_routes_for_server(server)
        LOGGER.info(f"VPN Server {server} is terminated")

    def get_status(self, server: "core_models.Server") -> ServerStatus:
        LOGGER.info(f"Get server status: {server}")
        return ServerStatus(state=ServerStateEnum.STOPPED)
