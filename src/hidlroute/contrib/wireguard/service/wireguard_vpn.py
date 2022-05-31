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

import datetime
import logging

from django.conf import settings
from django.utils import timezone
from django.utils.functional import cached_property
from pr2modules.netlink.generic.wireguard import WireGuard

from hidlroute.contrib.wireguard.models import WireguardServer
from hidlroute.contrib.wireguard.views import WireguardDeviceVPNConfigView
from hidlroute.core import models as core_models
from hidlroute.contrib.wireguard import models
from hidlroute.core.service.base import (
    HidlNetworkingException,
    WorkerService,
    JobStatus,
)
from hidlroute.vpn.service.base import ServerState, ServerStatus, VPNService, VPNServiceViews
from hidlroute.core.service.firewall.base import FirewallService
from hidlroute.core.service.networking.base import NetInterfaceState, InterfaceKind, NetworkingService

LOGGER = logging.getLogger("hidl_wireguard.WireguardVPNService")


class WireguardVPNViews(VPNServiceViews):
    @cached_property
    def vpn_details_view(self):
        return WireguardDeviceVPNConfigView.as_view()


class WireguardVPNService(VPNService):
    @staticmethod
    def __ensure_wg_server(server: "core_models.VpnServer") -> None:
        assert isinstance(server, WireguardServer), "WireguardVPNService can only take WireguardServer as an argument"

    def do_vpn_server_start(self, server: "models.WireguardServer"):
        self.__ensure_wg_server(server)
        net_service = server.service_factory.networking_service
        firewall_service: FirewallService = server.service_factory.firewall_service  # noqa

        try:
            # Setting up common networking
            interface = net_service.create_interface(ifname=server.interface_name, kind=InterfaceKind.WIREGUARD)
            net_service.add_ip_address(interface, server.ip_address)
            net_service.set_link_status(interface, NetInterfaceState.UP)

            wg = WireGuard()

            # Add a WireGuard configuration + first peer
            wg.set(interface.name, private_key=server.private_key, listen_port=server.listen_port)
            for peer in server.get_devices():
                peer = {"public_key": peer.public_key, "allowed_ips": [str(peer.ip_address)]}
                wg.set(interface.name, peer=peer)

            # Start routing
            self.setup_routes_for_server(server)
            # Start firewall
            firewall_service.setup_firewall_for_server(server)
        except Exception as start_exception:
            LOGGER.exception(f"Error starting server, see details below:\n{start_exception}")

            # Rolling firewall rules
            try:
                firewall_service.destroy_firewall_for_server(server)
            except Exception as e:
                LOGGER.exception("Encountered exception while firewall: " + str(e))

            # Rolling back routing rules
            try:
                self.destroy_routes_for_server(server)
            except Exception as e:
                LOGGER.exception("Encountered exception while rolling back routes: " + str(e))

            try:
                net_service.delete_interface(ifname=server.interface_name)
            except Exception as e:
                LOGGER.exception("Encountered exception while destroying interface: " + str(e))

            raise HidlNetworkingException(f"Error starting server: {str(start_exception)}") from start_exception

    def do_vpn_server_stop(self, server: "models.WireguardServer"):
        self.__ensure_wg_server(server)
        net_service: NetworkingService = server.service_factory.networking_service  # noqa
        firewall_service: FirewallService = server.service_factory.firewall_service  # noqa

        try:
            firewall_service.destroy_firewall_for_server(server)
        except Exception as e:
            LOGGER.exception(f"Enable to destroy firewall while terminating server {server}: {e}")
        try:
            self.destroy_routes_for_server(server)
        except Exception as e:
            LOGGER.exception(f"Enable to destroy routes while terminating server {server}: {e}")

        try:
            net_service.delete_interface(ifname=server.interface_name)
        except Exception as e:
            LOGGER.error(f"Error stopping interface, see details below: {e}")
            raise HidlNetworkingException(f"Error stopping interface: {str(e)}") from e

    def do_get_status(self, server: "models.WireguardServer") -> ServerStatus:
        self.__ensure_wg_server(server)
        net_service = server.service_factory.networking_service
        worker_service: WorkerService = server.service_factory.worker_service  # noqa
        interface = net_service.get_interface_by_name(server.interface_name)

        iface_state = (
            ServerState.RUNNING
            if (interface and interface.state == NetInterfaceState.UP.value)
            else ServerState.STOPPED
        )
        desired_state = server.desired_state or ServerState.STOPPED
        state = ServerState.UNKNOWN
        job_result = worker_service.get_job_result(server.state_change_job_id) if server.state_change_job_id else None
        if job_result is not None:
            if job_result.status == JobStatus.PENDING:
                tzinfo = timezone.get_current_timezone() if settings.USE_TZ else None
                timeout = datetime.timedelta(seconds=20)
                if (
                    server.state_change_job_start
                    and datetime.datetime.now(tz=tzinfo) - server.state_change_job_start > timeout
                ):
                    # Task is pending for too long. Consider as failed
                    state = ServerState.FAILED
                else:
                    if desired_state == ServerState.RUNNING:
                        state = ServerState.STARTING
                    elif desired_state == ServerState.STOPPED:
                        state = ServerState.STOPPING
            elif job_result.status == JobStatus.FAILED:
                state = ServerState.FAILED
            elif job_result.status == JobStatus.SUCCESS:
                state = iface_state

        if state == ServerState.FAILED and iface_state == ServerState.RUNNING:
            state = ServerState.UNKNOWN
        else:
            if state == ServerState.UNKNOWN:
                state = iface_state

        return ServerStatus(state=state)

    @cached_property
    def views(self) -> VPNServiceViews:
        return WireguardVPNViews()
