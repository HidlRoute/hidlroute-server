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

# Create your models here.
import polymorphic.models
from cidrfield.models import IPNetworkField
from django.conf import settings
from django.db import models
from treebeard import mp_tree


def should_be_single_IP(ip_network):
    return True


class Server(models.Model):
    interface_name = models.CharField(max_length=16)
    name = models.CharField(max_length=1024)


class Subnet(models.Model):
    server_group = models.ForeignKey("ServerGroup", on_delete=models.RESTRICT)
    name = models.CharField(max_length=1024)
    cidr = IPNetworkField()


class Group(mp_tree.MP_Node):
    DEFAULT_GROUP_ID = 1
    servers = models.ManyToManyField(Server, through="ServerGroup")
    name = models.CharField(max_length=1024)

    def __str__(self):
        return f"G: {self.name}"


class ServerGroup(models.Model):
    server = models.ForeignKey(Server, on_delete=models.RESTRICT)
    group = models.ForeignKey(Group, on_delete=models.RESTRICT)
    # subnet = models.ForeignKey(Subnet, on_delete=models.RESTRICT)


class Member(polymorphic.models.PolymorphicModel):
    group = models.ForeignKey(Group, on_delete=models.RESTRICT)
    servers = models.ManyToManyField(Server, through="ServerToMember")


class Person(Member):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=False, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"P: {self.user.username}"


class Host(Member):
    host_name = models.CharField(max_length=1024)


class ServerToMember(models.Model):
    server = models.ForeignKey(Server, on_delete=models.RESTRICT)
    member = models.ForeignKey(Member, on_delete=models.RESTRICT)


class Device(models.Model):
    server_member = models.ForeignKey(ServerToMember, on_delete=models.RESTRICT, null=True)
    address = IPNetworkField(validators=[should_be_single_IP])


class ServerRule(polymorphic.models.PolymorphicModel):
    server_group = models.ForeignKey(ServerGroup, on_delete=models.RESTRICT)
    server_member = models.ForeignKey(ServerToMember, on_delete=models.RESTRICT)


class ServerFirewallRule(ServerRule):
    action = models.CharField(max_length=16)


class ServerRoutingRule(ServerRule):
    network = IPNetworkField()
    gateway = IPNetworkField()
    interface = models.CharField(max_length=16)


class ClientConfig(models.Model):
    DNS = models.CharField(max_length=128)
