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

# from django.db import models

from cidrfield.models import IPNetworkField
from django.conf import settings
from django.db import models

# Create your models here.
from polymorphic import models as polymorphic_models
from treebeard import mp_tree

from hidlroute.core.base_models import Nameable, WithComment, Sortable


def should_be_single_IP(ip_network):
    return True


class Server(Nameable, WithComment, models.Model):
    interface_name = models.CharField(max_length=16)

    def __str__(self):
        return f"S: {self.name}"


class Subnet(Nameable, WithComment, models.Model):
    server_group = models.ForeignKey("ServerGroup", on_delete=models.RESTRICT)
    cidr = IPNetworkField()


class Group(Nameable, WithComment, mp_tree.MP_Node):
    DEFAULT_GROUP_SLUG = "x-default"
    servers = models.ManyToManyField(Server, through="ServerGroup")

    def __str__(self):
        return f"G: {self.name}"

    @classmethod
    def get_default_group(cls):
        return cls.objects.get(slug=cls.DEFAULT_GROUP_SLUG)


class ServerGroup(WithComment, models.Model):
    server = models.ForeignKey(Server, on_delete=models.RESTRICT)
    group = models.ForeignKey(Group, on_delete=models.RESTRICT)


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
    server = models.ForeignKey(Server, on_delete=models.RESTRICT)
    member = models.ForeignKey(Member, on_delete=models.RESTRICT)

    class Meta:
        unique_together = [("server", "member")]


class Device(WithComment, models.Model):
    server_member = models.ForeignKey(ServerToMember, on_delete=models.RESTRICT, null=True)
    address = IPNetworkField(validators=[should_be_single_IP])


class ServerRule(WithComment, polymorphic_models.PolymorphicModel):
    server_group = models.ForeignKey(ServerGroup, on_delete=models.RESTRICT, null=True, blank=True)
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
    network = IPNetworkField()
    gateway = IPNetworkField()
    interface = models.CharField(max_length=16)


class ClientConfig(models.Model):
    DNS = models.CharField(max_length=128)
