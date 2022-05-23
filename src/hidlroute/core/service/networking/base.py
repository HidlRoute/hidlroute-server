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
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Optional, List

from hidlroute.core.types import IpNetwork, IpAddress

if TYPE_CHECKING:
    from hidlroute.core import models


class NetworkVar(Enum):
    Self = "self"
    Any = "any"
    Host = "host"

    def __str__(self):
        return "Net({})".format(self.name)

    @classmethod
    def parse_str(cls, in_str: str) -> "NetworkVar":
        PREFIX = "$"
        in_str = in_str.lower().strip()
        if in_str.startswith(PREFIX):
            try:
                return NetworkVar[in_str[len(PREFIX) :]]
            except KeyError:
                raise ValueError("Unknown special var " + in_str)
        raise ValueError("Invalid special var " + in_str)


@dataclass
class Route:
    network: Optional[IpNetwork] = None
    interface: Optional[str] = None
    gateway: Optional[IpAddress] = None

    @property
    def is_default(self) -> bool:
        return self.network is None


class NetInterfaceStatus(Enum):
    UP = "UP"
    DOWN = "DOWN"


@dataclass
class NetInterface:
    name: str
    index: int
    state: NetInterfaceStatus
    mac_address: str
    ip4address: Optional[ipaddress.IPv4Address] = None
    ip6address: Optional[ipaddress.IPv6Address] = None

    @property
    def address(self) -> Optional[IpAddress]:
        if self.ip4address:
            return self.ip4address
        return self.ip6address


class NetworkingService(abc.ABC):
    @abc.abstractmethod
    def setup_routes_for_server(self, server: "models.Server"):
        pass

    @abc.abstractmethod
    def destroy_routes_for_server(self, server: "models.Server"):
        pass

    @abc.abstractmethod
    def get_routes(self) -> List[Route]:
        pass

    @abc.abstractmethod
    def get_default_routes(self) -> Optional[Route]:
        pass

    @abc.abstractmethod
    def get_interfaces(self) -> List[NetInterface]:
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
