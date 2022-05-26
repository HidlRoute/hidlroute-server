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
from typing import Optional, Union

from django.db import transaction

from hidlroute.core import models as models
from hidlroute.vpn import models as vpn_models
from hidlroute.core.errors import IpAddressUnavailable
from hidlroute.core.types import IpAddress

LOGGER = logging.getLogger("hidl_core.service.ip_allocation")


class IPAllocationService(object):
    def is_ip_available(self, ip_address: Union[str, IpAddress], server: vpn_models.VpnServer) -> bool:
        """
        Returns true if given address is available for allocation.
        """
        entities_count = (
            vpn_models.Device.objects.filter(ip_address=ip_address).count()
            + vpn_models.VpnServer.objects.filter(ip_address=ip_address).count()
        )
        return entities_count == 0

    @transaction.atomic
    def pick_ip_from_subnet(
        self, server: vpn_models.VpnServer, subnet: models.Subnet, allocate: bool = False
    ) -> IpAddress:
        """
        Returns the next available IP for the server subnet.
        If allocate is True, IPAllocationMeta will be updated.
        """
        ip_allocation_meta = server.get_ip_allocation_meta(subnet)
        candidate: Optional[IpAddress] = ip_allocation_meta.last_allocated_ip
        try:
            if candidate is None:
                candidate = ip_allocation_meta.last_allocated_ip = subnet.cidr.network_address + 1
                if candidate not in subnet.cidr:
                    raise IpAddressUnavailable("Exceeded IP range")
                while not self.is_ip_available(candidate, server):
                    candidate += 1

                if allocate:
                    ip_allocation_meta.last_allocated_ip = candidate
                    ip_allocation_meta.save()

                return candidate
        except Exception as e:
            raise IpAddressUnavailable("Unable to allocate ip for server {} subnet {}".format(server, subnet)) from e

    def allocate_ip(self, server: vpn_models.VpnServer, member: models.Member) -> IpAddress:
        """
        Allocates ip address for given member. IPAllocationMeta will be updated accordingly.
        """
        server_to_member = server.get_or_create_member(member)
        subnet = server_to_member.get_applicable_subnet()
        new_ip = self.pick_ip_from_subnet(server, subnet, allocate=True)
        return new_ip
