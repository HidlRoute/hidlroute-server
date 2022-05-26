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

from typing import TYPE_CHECKING

from django.db import models
from django.db.models import Q

if TYPE_CHECKING:
    from hidlroute.vpn import models as vpn_models


class ServerRelated(models.Model):
    """
    Base class to associate an entity with either server or server member
    """

    class Meta:
        abstract = True
        constraints = [
            models.CheckConstraint(
                check=models.Q(server_group__isnull=False, server_member__isnull=True, server__isnull=True)
                | models.Q(server_group__isnull=True, server_member__isnull=False, server__isnull=True)
                | models.Q(server_group__isnull=True, server_member__isnull=True, server__isnull=False),
                name="check_%(app_label)s_%(class)s_member_xor_group_xor_server",
            ),
        ]

    server = models.ForeignKey("VpnServer", on_delete=models.CASCADE, null=True, blank=True)
    server_group = models.ForeignKey("ServerToGroup", on_delete=models.CASCADE, null=True, blank=True)
    server_member = models.ForeignKey("ServerToMember", on_delete=models.CASCADE, null=True, blank=True)

    @classmethod
    def load_related_to_servermember(cls, server_to_member: "vpn_models.ServerToMember") -> models.QuerySet:
        group = server_to_member.member.group
        target_ids = [x.pk for x in list(group.get_ancestors()) + [group]]
        server_groups = server_to_member.server.servertogroup_set.filter(pk__in=target_ids)
        query = Q(server=server_to_member.server) | Q(server_member=server_to_member)
        if len(server_groups) > 0:
            query |= Q(server_group__in=server_groups)
        return cls.objects.filter(query).distinct()

    @classmethod
    def load_related_to_server(cls, server: "vpn_models.VpnServer") -> models.QuerySet:
        return cls.objects.filter(
            Q(server=server) | Q(server_group__server=server) | Q(server_member__server=server)
        ).distinct()
