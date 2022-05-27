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
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List

from hidlroute.core.types import IpNetwork, IpAddress, NetworkDef


class NetVar(Enum):
    Self = "self"  # Ip address of the vpn server
    Server = "server"  # All subnets routed via current server interface
    Any = "any"  # Anything
    Host = "host"  # Any IP address associated with the host except this vpn

    def __str__(self):
        return "Net({})".format(self.name)

    @classmethod
    def parse_str(cls, in_str: str) -> "NetVar":
        PREFIX = "$"
        in_str = in_str.lower().strip()
        if in_str.startswith(PREFIX):
            try:
                return NetVar(in_str[len(PREFIX) :])
            except ValueError:
                raise ValueError("Unknown special var " + in_str)
        raise ValueError("Invalid special var " + in_str)


class InterfaceKind(Enum):
    WIREGUARD = "wireguard"


@dataclass
class Route:
    network: Optional[IpNetwork] = None
    interface: Optional[str] = None
    gateway: Optional[IpAddress] = None

    @property
    def is_default(self) -> bool:
        return self.network is None


class NetInterfaceState(Enum):
    UP = "up"
    DOWN = "down"


@dataclass
class NetInterface:
    name: str
    index: int
    state: NetInterfaceState
    mac_address: str
    ip4address: Optional[ipaddress.IPv4Address] = None
    ip6address: Optional[ipaddress.IPv6Address] = None

    @property
    def address(self) -> Optional[IpAddress]:
        if self.ip4address:
            return self.ip4address
        return self.ip6address

    def __str__(self) -> str:
        return f"NetIface({self.name}, ip={self.address}, state={self.state}, mac={self.mac_address})"


@dataclass
class NetworkContext:
    server_ip: IpAddress
    server_networks: List[IpNetwork] = field(default_factory=list)
    host_networks: List[IpNetwork] = field(default_factory=list)

    def belongs_to_server(self, net: IpNetwork) -> bool:
        for x in self.server_networks:
            if net is None or (x.version == net.version and x.supernet_of(net)):
                return True
        return False

    def belongs_to_host(self, net: IpNetwork) -> bool:
        for x in self.host_networks:
            if net is None or (x.version == net.version and x.supernet_of(net)):
                return True
        return False


class NetworkingService(abc.ABC):
    @abc.abstractmethod
    def create_route(self, route: Route) -> Route:
        pass

    @abc.abstractmethod
    def delete_route(self, route: Route):
        pass

    @abc.abstractmethod
    def get_routes(self) -> List[Route]:
        pass

    @abc.abstractmethod
    def get_default_routes(self) -> List[Route]:
        pass

    @abc.abstractmethod
    def get_interfaces(self) -> List[NetInterface]:
        pass

    @abc.abstractmethod
    def create_interface(self, ifname: str, kind: InterfaceKind) -> NetInterface:
        pass

    @abc.abstractmethod
    def delete_interface(self, ifname: str) -> None:
        pass

    @abc.abstractmethod
    def add_ip_address(self, interface: NetInterface, address: IpAddress) -> None:
        pass

    @abc.abstractmethod
    def set_link_status(self, interface: NetInterface, status: NetInterfaceState) -> None:
        pass

    def get_interface_by_name(self, iface_name: str) -> Optional[NetInterface]:
        for x in self.get_interfaces():
            if x.name == iface_name:
                return x

    def get_interfaces_by_name_prefix(self, prefix: str) -> List[NetInterface]:
        result: List[NetInterface] = []
        for x in self.get_interfaces():
            if x.name.startswith(prefix):
                result.append(x)
        return result

    def resolve_subnets(self, networks: List[NetworkDef], network_context: NetworkContext) -> List[Optional[IpNetwork]]:
        result: List[Optional[IpNetwork]] = []
        for x in networks:
            if isinstance(x, NetVar):
                if x == NetVar.Self:
                    result += ipaddress.ip_network(str(network_context.server_ip))
                elif x == NetVar.Host:
                    result += network_context.host_networks
                elif x == NetVar.Server:
                    result += network_context.server_networks
                elif x == NetVar.Any:
                    result.append(None)
                else:
                    raise ValueError("Unknown network var {}".format(x))
            else:
                result.append(x)
        return result
