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
from io import BytesIO
from typing import Optional, Type, io

import logging
from autoslug.settings import slugify
from django.contrib.postgres.indexes import GistIndex
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db import models, transaction
import netfields

from polymorphic import models as polymorphic_models
from treebeard import mp_tree

from hidlroute.core.base_models import NameableIdentifiable, WithComment, Sortable, ServerRelated
from hidlroute.core.factory import service_factory
from hidlroute.core.types import IpAddress

LOGGER = logging.getLogger("hidl_core.models")


class Subnet(NameableIdentifiable, WithComment, models.Model):
    cidr = netfields.CidrAddressField()

    def __str__(self) -> str:
        return f"{self.name} ({self.cidr})"


class Server(NameableIdentifiable, WithComment, polymorphic_models.PolymorphicModel):
    interface_name = models.CharField(max_length=16)
    ip_address = netfields.InetAddressField(null=False, blank=False)
    subnet = models.ForeignKey(Subnet, on_delete=models.RESTRICT)

    def __str__(self):
        return f"S: {self.name}"

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None) -> None:
        is_creating = self.pk is None
        super().save(force_insert, force_update, using, update_fields)
        # If there are no any client routing rules, create default one to route all traffic to
        # the server subnet via VPN interface
        if is_creating and self.clientroutingrule_set.all().count() == 0:
            default_client_rule = ClientRoutingRule.objects.create(
                server=self, network=self.subnet, comment=_("Route main server subnet to the vpn tunnel")
            )
            self.clientroutingrule_set.add(default_client_rule)

    def get_or_create_member(self, member: "Member") -> "ServerToMember":
        return ServerToMember.get_or_create(self, member)

    def allocate_ip_for_member(self, member: "Member") -> str:
        service_factory.ip_allocation_service.allocate_ip(self, member)

    def get_ip_allocation_meta(self, subnet: Subnet) -> "IpAllocationMeta":
        return IpAllocationMeta.objects.get_or_create(server=self, subnet=subnet)[0]

    @classmethod
    def get_device_model(cls) -> Type["Device"]:
        raise NotImplementedError


class IpAllocationMeta(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    subnet = models.ForeignKey(Subnet, on_delete=models.RESTRICT)
    last_allocated_ip = netfields.InetAddressField(null=True, blank=True)

    class Meta:
        unique_together = [("server", "subnet")]


class Group(NameableIdentifiable, WithComment, mp_tree.MP_Node):
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

    def __str__(self) -> str:
        return str(self.group)


class Member(WithComment, polymorphic_models.PolymorphicModel):
    group = models.ForeignKey(Group, on_delete=models.RESTRICT)
    servers = models.ManyToManyField(Server, through="ServerToMember")

    def __str__(self) -> str:
        return str(self.get_real_instance())

    def get_name(self) -> str:
        raise NotImplementedError


class Person(Member):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=False, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"P: {self.user.username}"

    def get_name(self) -> str:
        return self.user.name


class Host(Member):
    host_name = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return f"H: {self.host_name}"

    def get_name(self) -> str:
        return self.host_name


class ServerToMember(models.Model):
    class Meta:
        verbose_name = _("Member")
        verbose_name_plural = _("Members")
        unique_together = [("server", "member")]

    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.RESTRICT)
    subnet = models.ForeignKey(Subnet, on_delete=models.RESTRICT, null=True, blank=True)

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None) -> None:
        super().save(force_insert, force_update, using, update_fields)
        if self.member.get_real_instance_class() == Host:
            Device.create_device_for_host(self.member.get_real_instance(), self.server)

    @classmethod
    def is_valid_member(cls, server: Server, member: Member) -> bool:
        if ServerToMember.objects.filter(server=server, member=member).exists():
            return True
        if server.servertogroup_set.filter(group=member.group).exists():
            return True
        return False

    @classmethod
    def get_or_create(cls, server: Server, member: Member) -> "ServerToMember":
        if cls.is_valid_member(server, member):
            return cls.objects.get_or_create(server=server, member=member)[0]
        raise PermissionDenied("{} is not allowed at server {}".format(member, server.name))

    def get_applicable_subnet(self) -> Subnet:
        if self.subnet is not None:
            return self.subnet
        try:
            server_to_group: Optional[ServerToGroup] = self.server.servertogroup_set.get(group=self.member.group)
        except ServerToGroup.DoesNotExist:
            server_to_group = None
        if server_to_group is not None and server_to_group.subnet is not None:
            return server_to_group.subnet
        return self.server.subnet

    def __str__(self) -> str:
        return str(self.member)


class DeviceConfig(abc.ABC):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

    @abc.abstractmethod
    def as_stream(self) -> io.IO:
        pass

    @abc.abstractmethod
    def as_str(self) -> str:
        pass


class SimpleTextDeviceConfig(DeviceConfig):
    def __init__(self, content: str, name: str) -> None:
        super().__init__()
        self.content = content
        self._name = name

    def as_stream(self) -> BytesIO:
        return BytesIO(self.content.encode("utf-8"))

    def as_str(self) -> str:
        return self.content

    @property
    def name(self) -> str:
        return self._name


class Device(NameableIdentifiable, WithComment, polymorphic_models.PolymorphicModel):
    class Meta:
        indexes = (GistIndex(fields=("ip_address",), opclasses=("inet_ops",), name="hidl_device_ipaddress_idx"),)

    server_to_member = models.ForeignKey(ServerToMember, on_delete=models.CASCADE, null=False, blank=True)
    ip_address = netfields.InetAddressField(null=False, blank=True, unique=True)
    mac_address = netfields.MACAddressField(null=True, blank=True)

    @classmethod
    @transaction.atomic
    def create_device_for_host(cls, host: Host, server: Server) -> "Device":
        server_to_member = ServerToMember.get_or_create(server=server, member=host)
        ip = service_factory.ip_allocation_service.allocate_ip(server_to_member.server, server_to_member.member)
        device = server.get_device_model().create_default(server_to_member=server_to_member, ip_address=ip)
        return device

    @classmethod
    def create_default(cls, server_to_member: ServerToMember, ip_address: IpAddress) -> "Device":
        raise NotImplementedError

    @classmethod
    def generate_name(cls, server: Server, member: Member) -> str:
        return slugify("-".join((member.get_real_instance().get_name(), server.slug)))

    def generate_config(self) -> DeviceConfig:
        raise NotImplementedError

    def get_client_routing_rules(self) -> QuerySet["ClientRoutingRule"]:
        return ClientRoutingRule.load_related_to_servermember(self.server_to_member)

    def __str__(self) -> str:
        return f"{self.name}"


class ServerRule(WithComment, ServerRelated):
    class Meta(ServerRelated.Meta):
        abstract = True


class ServerFirewallRule(Sortable, ServerRule):
    action = models.CharField(max_length=16)

    def __str__(self):
        return f"{self.action} {self.comment}"


class ServerRoutingRule(ServerRule):
    network = models.ForeignKey(Subnet, null=True, blank=True, on_delete=models.CASCADE)
    gateway = netfields.InetAddressField(null=True, blank=True)
    interface = models.CharField(
        max_length=16,
        null=True,
        blank=True,
    )


class ClientRule(WithComment, ServerRelated):
    class Meta(ServerRelated.Meta):
        abstract = True


class ClientRoutingRule(ClientRule):
    network = models.ForeignKey(Subnet, null=False, blank=False, on_delete=models.CASCADE)
