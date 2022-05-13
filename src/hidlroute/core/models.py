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


def should_be_single_IP(ip_network):
    return True


class Server(models.Model):
    interface_name = models.CharField(max_length=16)
    name = models.CharField(max_length=1024)


class Subnet(models.Model):
    server_group = models.ForeignKey("ServerGroup", on_delete=models.RESTRICT)
    name = models.CharField(max_length=1024)
    cidr = IPNetworkField()


class Group(models.Model):
    parent_group = models.ForeignKey("self", on_delete=models.RESTRICT, null=True)
    servers = models.ManyToManyField(Server, through="ServerGroup")


class ServerGroup(models.Model):
    server = models.ForeignKey(Server, on_delete=models.RESTRICT)
    group = models.ForeignKey(Group, on_delete=models.RESTRICT)
    # subnet = models.ForeignKey(Subnet, on_delete=models.RESTRICT)


class Member(models.Model):
    group = models.ForeignKey(Group, on_delete=models.RESTRICT)
    name = models.CharField(max_length=1024)
    servers = models.ManyToManyField(Server, through="ServerMember")


class ServerMember(polymorphic.models.PolymorphicModel):
    server_group = models.ForeignKey(ServerGroup, on_delete=models.RESTRICT)
    server = models.ForeignKey(Server, on_delete=models.RESTRICT)
    member = models.ForeignKey(Member, on_delete=models.RESTRICT)


class Person(ServerMember):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=False, on_delete=models.CASCADE)
    pass


class Host(ServerMember):
    host_name = models.CharField(max_length=1024)
    pass


class Device(models.Model):
    server_member = models.ForeignKey(ServerMember, on_delete=models.RESTRICT, null=True)
    address = IPNetworkField(validators=[should_be_single_IP])


class ServerRule(polymorphic.models.PolymorphicModel):
    server_group = models.ForeignKey(ServerGroup, on_delete=models.RESTRICT)
    server_member = models.ForeignKey(ServerMember, on_delete=models.RESTRICT)


class ServerFirewallRule(ServerRule):
    action = models.CharField(max_length=16)


class ServerRoutingRule(ServerRule):
    network = IPNetworkField()
    gateway = IPNetworkField()
    interface = models.CharField(max_length=16)


class ClientConfig(models.Model):
    DNS = models.CharField(max_length=128)
