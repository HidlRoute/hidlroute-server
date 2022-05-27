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

import abc
import ipaddress
from enum import Enum
from typing import TYPE_CHECKING, List

from django.utils.translation import gettext_lazy as _

from hidlroute.core.service.networking.base import Route
from hidlroute.core.types import IpNetwork
from hidlroute.core.utils import django_enum

if TYPE_CHECKING:
    from hidlroute.vpn import models


@django_enum
class ServerState(Enum):
    STOPPED = 0x100
    RUNNING = 0x101
    FAILED = 0x102

    STOPPING = 0x200
    STARTING = 0x201
    UNKNOWN = 0xFFF  # Indicates inconsistent state

    __labels__ = {
        STOPPED: _("Stopped"),
        RUNNING: _("Running"),
        FAILED: _("Failed"),
        STOPPING: _("Stopping"),
        STARTING: _("Starting"),
        UNKNOWN: _("Unknown"),
    }

    @property
    def label(self) -> str:
        if self in ServerState.__labels__:
            return ServerState.__labels__[self]
        return self.name

    @property
    def is_running(self) -> bool:
        return self == self.RUNNING

    @property
    def is_transitioning(self) -> bool:
        return self in (self.STARTING, self.STOPPING)


class ServerStatus:
    def __init__(self, state: ServerState) -> None:
        self.state = state


class VPNService(abc.ABC):
    @abc.abstractmethod
    def start(self, server: "models.VpnServer"):
        pass

    @abc.abstractmethod
    def stop(self, server: "models.VpnServer"):
        pass

    @abc.abstractmethod
    def get_status(self, server: "models.VpnServer") -> ServerStatus:
        pass

    def restart(self, server: "models.VpnServer"):
        job = server.stop()
        server.service_factory.worker_service.wait_for_job(job.uuid)
        server = server.__class__.objects.get(pk=server.pk)  # Force reload from DB and new instance to clear all caches
        job = server.start()
        server.service_factory.worker_service.wait_for_job(job.uuid)

    def _server_routing_rule_to_route(
            self, routing_rule: "models.ServerRoutingRule", server: "models.VpnServer"
    ) -> Route:
        return Route(
            network=routing_rule.network.cidr,
            gateway=routing_rule.gateway,
            interface=routing_rule.resolved_interface_name(server),
        )

    def setup_routes_for_server(self, server: "models.VpnServer"):
        networking_service = server.service_factory.networking_service
        for routing_rule in server.get_routing_rules():
            route = self._server_routing_rule_to_route(routing_rule, server)
            networking_service.create_route(route)

    def destroy_routes_for_server(self, server: "models.VpnServer"):
        networking_service = server.service_factory.networking_service
        for routing_rule in server.get_routing_rules():
            route = self._server_routing_rule_to_route(routing_rule, server)
            networking_service.delete_route(route)

    def get_routes_for_server(self, server: "models.VpnServer") -> List[Route]:
        networking_service = server.service_factory.networking_service
        result: List[Route] = []
        for r in networking_service.get_routes():
            if r.interface == server.interface_name:
                result.append(r)
        return result

    def get_subnets_for_server(self, server: "models.VpnServer") -> List[IpNetwork]:
        networking_service = server.service_factory.networking_service
        return [r.network for r in networking_service.get_routes_for_server(server)]

    # TODO: Remove me to get_non_server_networks
    def get_host_networks(self, server: "models.VpnServer") -> List[IpNetwork]:
        networking_service = server.service_factory.networking_service
        result: List[IpNetwork] = []
        for x in networking_service.get_interfaces():
            if x.name != server.interface_name:
                result.append(ipaddress.ip_network(str(x.address)))
        return result
