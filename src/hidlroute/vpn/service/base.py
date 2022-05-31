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
import datetime
import ipaddress
from enum import Enum
from typing import TYPE_CHECKING, List

from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from hidlroute.core.service.base import WorkerService, JobStatus, PostedJob
from hidlroute.core.service.networking.base import Route
from hidlroute.core.types import IpNetwork
from hidlroute.core.utils import django_enum
from hidlroute.vpn import const
from hidlroute.vpn.views import BaseVPNDeviceConfigView

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

    def to_dict(self) -> dict:
        return dict(state=self.state.name)

    @classmethod
    def from_dict(cls, obj: dict) -> "ServerStatus":
        return ServerStatus(state=ServerState[obj["state"]])


class VPNServiceViews(object):
    @cached_property
    def vpn_details_view(self) -> BaseVPNDeviceConfigView:
        raise NotImplementedError


class VPNService(abc.ABC):
    @abc.abstractmethod
    def do_vpn_server_start(self, server: "models.VpnServer"):
        pass

    @abc.abstractmethod
    def do_vpn_server_stop(self, server: "models.VpnServer"):
        pass

    @abc.abstractmethod
    def do_get_status(self, server: "models.VpnServer") -> ServerStatus:
        pass

    def do_vpn_server_restart(self, server: "models.VpnServer"):
        self.do_vpn_server_stop(server)
        self.do_vpn_server_start(server)

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
        return [r.network for r in server.vpn_service.get_routes_for_server(server)]

    def get_non_server_networks(self, server: "models.VpnServer") -> List[IpNetwork]:
        networking_service = server.service_factory.networking_service
        result: List[IpNetwork] = []
        for x in networking_service.get_interfaces():
            if x.name != server.interface_name:
                result.append(ipaddress.ip_network(str(x.address)))
        return result

    @property
    @abc.abstractmethod
    def views(self) -> VPNServiceViews:
        raise NotImplementedError

    def get_server_status(self, server: "models.VpnServer") -> ServerStatus:
        worker_service: WorkerService = server.service_factory.worker_service  # noqa
        job = worker_service.post_job(const.JOB_ID_GET_VPN_SERVER_STATUS, server.pk)
        job_result = worker_service.wait_for_job(job.uuid, timeout=datetime.timedelta(seconds=3))
        if job_result.status == JobStatus.SUCCESS:
            return ServerStatus.from_dict(job_result.result)
        raise Exception(f"Unable to get status for {server.name}: {str(job_result.result)}")

    def start_vpn_server(self, server: "models.VpnServer") -> PostedJob:
        worker_service: WorkerService = server.service_factory.worker_service  # noqa
        return worker_service.post_job(const.JOB_ID_START_VPN_SERVER, server.pk)

    def stop_vpn_server(self, server: "models.VpnServer") -> PostedJob:
        worker_service: WorkerService = server.service_factory.worker_service  # noqa
        return worker_service.post_job(const.JOB_ID_STOP_VPN_SERVER, server.pk)

    def restart_vpn_server(self, server: "models.VpnServer") -> PostedJob:
        worker_service: WorkerService = server.service_factory.worker_service  # noqa
        server.desired_state = ServerState.RUNNING
        job = worker_service.post_job(const.JOB_ID_RESTART_VPN_SERVER, server.pk)
        server.state_change_job_id = job.uuid
        server.state_change_job_start = job.timestamp
        server.save()
        return job
