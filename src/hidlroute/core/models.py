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

from django.contrib.postgres.indexes import GistIndex
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db import models
import netfields

from polymorphic import models as polymorphic_models
from treebeard import mp_tree

from hidlroute.core.base_models import Nameable, WithComment, Sortable
from hidlroute.core.factory import service_factory


def should_be_single_IP(ip_network):
    return True


class Subnet(Nameable, WithComment, models.Model):
    cidr = netfields.CidrAddressField()

    def __str__(self) -> str:
        return f"{self.name} ({self.cidr})"


class Server(Nameable, WithComment, polymorphic_models.PolymorphicModel):
    interface_name = models.CharField(max_length=16)
    ip_address = models.GenericIPAddressField(null=False, blank=False)
    subnet = models.ForeignKey(Subnet, on_delete=models.RESTRICT)

    def __str__(self):
        return f"S: {self.name}"

    def allocate_ip_for_member(self, member: "Member") -> str:
        service_factory.ip_allocation_service.allocate_ip(self, member)


class IpAllocation(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    subnet = models.ForeignKey(Subnet, on_delete=models.RESTRICT)
    last_allocated_ip = netfields.InetAddressField(null=True, blank=True)

    class Meta:
        unique_together = [("server", "subnet")]


class Group(Nameable, WithComment, mp_tree.MP_Node):
    DEFAULT_GROUP_SLUG = "x-default"
    servers = models.ManyToManyField(Server, through="ServerToGroup")

    def __str__(self):
        return f"G: {self.name}"

    @classmethod
    def get_default_group(cls):
        return cls.objects.get(slug=cls.DEFAULT_GROUP_SLUG)


class ServerToGroup(models.Model):
    class Meta:
        verbose_name = _("Group")
        verbose_name_plural = _("Groups")
        unique_together = [("server", "group")]

    server = models.ForeignKey(Server, on_delete=models.RESTRICT)
    group = models.ForeignKey(Group, on_delete=models.RESTRICT)
    subnet = models.ForeignKey(Subnet, on_delete=models.RESTRICT, null=True, blank=True)


class Member(WithComment, polymorphic_models.PolymorphicModel):
    group = models.ForeignKey(Group, on_delete=models.RESTRICT)
    servers = models.ManyToManyField(Server, through="ServerToMember")

    def __str__(self) -> str:
        return str(self.get_real_instance())


class Person(Member):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=False, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"P: {self.user.username}"


class Host(Member):
    host_name = models.SlugField(max_length=100)

    def __str__(self):
        return f"H: {self.host_name}"


class ServerToMember(models.Model):
    class Meta:
        verbose_name = _("Member")
        verbose_name_plural = _("Members")
        unique_together = [("server", "member")]

    server = models.ForeignKey(Server, on_delete=models.RESTRICT)
    member = models.ForeignKey(Member, on_delete=models.RESTRICT)
    subnet = models.ForeignKey(Subnet, on_delete=models.RESTRICT, null=True, blank=True)

    def __str__(self) -> str:
        return "S2M: " + str(self.member)


class Device(WithComment, polymorphic_models.PolymorphicModel):
    server_member = models.ForeignKey(ServerToMember, on_delete=models.RESTRICT, null=False, blank=True)
    ip_address = netfields.InetAddressField(null=False, blank=True)
    mac_address = netfields.MACAddressField(null=True, blank=True)

    class Meta:
        indexes = (GistIndex(fields=("ip_address",), opclasses=("inet_ops",), name="hidl_device_ipaddress_idx"),)


class ServerRule(WithComment, polymorphic_models.PolymorphicModel):
    server_group = models.ForeignKey(ServerToGroup, on_delete=models.RESTRICT, null=True, blank=True)
    server_member = models.ForeignKey(ServerToMember, on_delete=models.RESTRICT, null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(server_group__isnull=True, server_member__isnull=False)
                | models.Q(server_group__isnull=False, server_member__isnull=True),
                name="check_serverrule_for_member_xor_group",
            ),
        ]


class ServerFirewallRule(Sortable, ServerRule):
    action = models.CharField(max_length=16)

    def __str__(self):
        return f"{self.action} {self.comment}"


class ServerRoutingRule(ServerRule):
    network = netfields.CidrAddressField()
    gateway = netfields.InetAddressField()
    interface = models.CharField(max_length=16)


class ClientConfig(models.Model):
    DNS = models.CharField(max_length=128)
