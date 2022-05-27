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

import ipaddress
import logging
from socket import AF_INET, AF_INET6
from typing import List, Optional

from pr2modules.netlink import NetlinkError
from pr2modules.netlink.rtnl.ifaddrmsg import ifaddrmsg as IF_ADDR
from pr2modules.netlink.rtnl.rtmsg import rtmsg as RT_MSG
from pr2modules.iproute import IPRoute

from hidlroute.core.service.networking.base import (
    NetworkingService,
    Route,
    NetInterface,
    InterfaceKind,
    NetInterfaceState,
)
from hidlroute.core.types import IpAddress

LOGGER = logging.getLogger("hidl_core.service.networking.pyroute2")


class PyRoute2NetworkingService(NetworkingService):
    def __ifaddr_to_ipaddress(self, addrmsg: IF_ADDR) -> IpAddress:
        addr_family = addrmsg.get("family")
        addr_str = addrmsg.get_attr("IFA_ADDRESS")
        if addr_family == AF_INET:
            return ipaddress.IPv4Address(addr_str)
        elif addr_family == AF_INET6:
            return ipaddress.IPv6Address(addr_str)
        raise ValueError("Unknown address family {}".format(addr_family))

    def __rtmsg_to_route(self, rtmsg: RT_MSG) -> Route:
        iface_idx = rtmsg.get_attr("RTA_OIF")
        route = Route(
            network=None, gateway=rtmsg.get_attr("RTA_GATEWAY"), interface=self.get_interface_by_idx(iface_idx)
        )
        return route

    def __ifmsg_to_interface(self, ifmsg) -> NetInterface:
        return NetInterface(
            name=ifmsg.get_attr("IFLA_IFNAME"),
            index=ifmsg.get("index"),
            state=ifmsg.get("state"),
            mac_address=ifmsg.get_attr("IFLA_ADDRESS"),
        )

    def __attach_ip_to_interface(self, iface: NetInterface, ipr: IPRoute) -> NetInterface:
        for x in ipr.get_addr(index=iface.index):
            addr_family = x.get("family")
            addr = self.__ifaddr_to_ipaddress(x)
            if addr_family == AF_INET:
                iface.ip4address = addr
            elif addr_family == AF_INET6:
                iface.ip6address = addr
        return iface

    def create_route(self, route: Route) -> Route:
        with IPRoute() as ipr:
            oif_index = self.get_interface_by_name(route.interface).index
            ipr.route("add", dst=str(route.network), gateway=route.gateway, oif=oif_index)
            return route

    def delete_route(self, route: Route):
        with IPRoute() as ipr:
            oif_index = self.get_interface_by_name(route.interface).index
            ipr.route("del", dst=str(route.network), gateway=route.gateway, oif=oif_index)

    def get_default_routes(self) -> List[Route]:
        result: List[Route] = []
        with IPRoute() as ipr:
            for r in ipr.get_default_routes():
                result.append(self.__rtmsg_to_route(r))
        return result

    def get_routes(self) -> List[Route]:
        result: List[Route] = []
        with IPRoute() as ipr:
            for r in ipr.get_routes():
                result.append(self.__rtmsg_to_route(r))
        return result

    def get_interfaces(self) -> List[NetInterface]:
        with IPRoute() as ipr:
            return [self.__attach_ip_to_interface(self.__ifmsg_to_interface(x), ipr) for x in ipr.get_links()]

    def get_interface_by_idx(self, idx: int) -> Optional[NetInterface]:
        try:
            with IPRoute() as ipr:
                for x in ipr.get_links(idx):
                    return self.__attach_ip_to_interface(self.__ifmsg_to_interface(x), ipr)
        except NetlinkError:
            return None
        return None

    def get_interface_by_name(self, iface_name: str) -> Optional[NetInterface]:
        with IPRoute() as ipr:
            links = [
                self.__attach_ip_to_interface(self.__ifmsg_to_interface(x), ipr)
                for x in ipr.get_links(ifname=iface_name)
            ]
            if len(links) > 0:
                return links[0]
        return None

    def create_interface(self, ifname: str, kind: InterfaceKind) -> NetInterface:
        with IPRoute() as ipr:
            ipr.link("add", kind=kind.value, ifname=ifname)
            return self.get_interface_by_name(ifname)

    def delete_interface(self, ifname: str) -> None:
        with IPRoute() as ipr:
            ipr.link("del", ifname=ifname)

    def add_ip_address(self, interface: NetInterface, address: IpAddress) -> None:
        with IPRoute() as ipr:
            ipr.addr(
                "add",
                index=self.get_interface_by_name(interface.name).index,
                address=str(address.ip),
                mask=address.max_prefixlen,
            )

    def set_link_status(self, interface: NetInterface, status: NetInterfaceState) -> None:
        with IPRoute() as ipr:
            ipr.link("set", index=self.get_interface_by_name(interface.name).index, state=status.value)
