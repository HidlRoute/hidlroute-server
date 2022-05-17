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

from django.db import transaction

from hidlroute.core import models
from hidlroute.core.types import IpAddress

LOGGER = logging.getLogger("hidl_core.service.ip_allocation")


class IpAddressUnavailable(Exception):
    pass


@transaction.atomic
def pick_ip_from_subnet(server: models.Server, subnet: models.Subnet) -> IpAddress:
    # Device.objects.filter(server_member__server=server, ip_address__net_contained=subnet.cidr).order('address')
    ip_allocation = models.IpAllocation.objects.get_or_create(server=server, subnet=subnet)
    # candidate = ip_allocation.last_allocated_ip
    pass


def allocate_ip(server: models.Server, member: models.Member) -> str:
    pass
