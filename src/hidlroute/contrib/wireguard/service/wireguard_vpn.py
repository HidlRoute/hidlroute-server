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

from pr2modules.netlink.generic.wireguard import WireGuard

from hidlroute.contrib.wireguard.models import WireguardServer
from hidlroute.core import models as core_models
from hidlroute.contrib.wireguard import models
from hidlroute.core.service.base import VPNService, ServerStateEnum, ServerStatus, HidlNetworkingException
from hidlroute.core.service.networking.base import NetInterfaceStatus, InterfaceKind

LOGGER = logging.getLogger("hidl_wireguard.WireguardVPNService")


class WireguardVPNService(VPNService):
    @staticmethod
    def __ensure_wg_server(server: "core_models.Server") -> None:
        assert isinstance(server, WireguardServer), "WireguardVPNService can only take WireguardServer as an argument"

    def start(self, server: "models.WireguardServer"):
        self.__ensure_wg_server(server)

        try:
            # Setting up common networking
            net_service = server.service_factory.networking_service
            interface = net_service.create_interface(ifname=server.interface_name, kind=InterfaceKind.WIREGUARD)
            net_service.add_ip_address(interface, server.ip_address)
            net_service.set_link_status(interface, NetInterfaceStatus.UP)

            wg = WireGuard()

            # Add a WireGuard configuration + first peer
            wg.set(interface.name, private_key=server.private_key, listen_port=server.listen_port)
            for peer in server.get_devices():
                peer = {"public_key": peer.public_key, "allowed_ips": [str(peer.ip_address)]}
                wg.set(interface.name, peer=peer)

            # Start routing
            net_service.setup_routes_for_server(server)

            # todo: Start firewall
        except Exception as e:
            LOGGER.error(f"Error starting server, see details below:\n{e}")
            LOGGER.exception(e)
            raise HidlNetworkingException(f"Error starting server: {str(e)}") from e

    def stop(self, server: "models.WireguardServer"):
        self.__ensure_wg_server(server)

        try:
            net_service = server.service_factory.networking_service
            net_service.destroy_routes_for_server(server)

            # todo: Stop firewall
            net_service.delete_interface(ifname=server.interface_name)

        except Exception as e:
            LOGGER.error(f"Error stopping interface, see details below:\n{e}")
            raise HidlNetworkingException(f"Error stopping interface: {str(e)}") from e

    def get_status(self, server: "models.WireguardServer") -> ServerStatus:
        self.__ensure_wg_server(server)
        net_service = server.service_factory.networking_service
        interface = net_service.get_interface_by_name(server.interface_name)

        # todo how should we handle FAILED status here? some error flag/logs?
        if not interface:
            return ServerStatus(state=ServerStateEnum.STOPPED)

        # todo what extra checks do we need here?
        if interface.state == NetInterfaceStatus.UP.value:
            return ServerStatus(state=ServerStateEnum.RUNNING)

        return ServerStatus(state=ServerStateEnum.STOPPED)
