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
import logging
from io import BytesIO

import netfields
from django.contrib.postgres.indexes import GistIndex
from django.core.exceptions import PermissionDenied
from django.db import models, transaction
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from typing import io, List, Optional, Type

from social_core.utils import slugify

from hidlroute.core.base_models import WithReprCache, WithComment, NameableIdentifiable
from hidlroute.core.models import BaseRoutingRule
from hidlroute.vpn.base_models import ServerRelated
from hidlroute.core import models as core_models

from hidlroute.core.service.networking.base import NetVar
from hidlroute.core.types import NetworkDef, IpAddress
from polymorphic import models as polymorphic_models
from django.contrib.auth.models import AbstractUser as DjangoUser
from hidlroute.core.service.base import PostedJob, JobResult
from hidlroute.vpn.factory import default_vpn_service_factory, VPNServiceFactory
from hidlroute.vpn.service.base import ServerState, ServerStatus, VPNService

LOGGER = logging.getLogger("hidl_vpn.models")


class IpAllocationMeta(models.Model):
    server = models.ForeignKey("VpnServer", on_delete=models.CASCADE)
    subnet = models.ForeignKey(core_models.Subnet, on_delete=models.RESTRICT)
    last_allocated_ip = netfields.InetAddressField(null=True, blank=True)

    class Meta:
        unique_together = [("server", "subnet")]


class ServerToGroup(models.Model):
    class Meta:
        verbose_name = _("Server Group")
        verbose_name_plural = _("Server Groups")
        unique_together = [("server", "group")]

    server = models.ForeignKey("VpnServer", on_delete=models.CASCADE)
    group = models.ForeignKey(core_models.Group, on_delete=models.RESTRICT)
    subnet = models.ForeignKey(core_models.Subnet, on_delete=models.RESTRICT, null=True, blank=True)

    def __str__(self) -> str:
        return str(self.group.get_full_name())

    def resolve_subnet(self) -> core_models.Subnet:
        if self.subnet:
            return self.subnet
        else:
            return self.server.subnet


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


class VpnNetworkFilter(WithReprCache, models.Model):
    subnet = models.ForeignKey(
        core_models.Subnet, null=True, blank=True, on_delete=models.RESTRICT, related_name="network_from"
    )
    custom = models.CharField(max_length=100, null=True, blank=True)
    server_group = models.ForeignKey("ServerToGroup", on_delete=models.CASCADE, null=True, blank=True)
    server_member = models.ForeignKey("ServerToMember", on_delete=models.CASCADE, null=True, blank=True)

    def parse_custom(self, server: "VpnServer") -> NetworkDef:
        for x in self.custom.split(","):
            x = x.strip().lower()
            try:
                return NetVar.parse_str(x)
            except ValueError:
                try:
                    return ipaddress.ip_network(self.custom, strict=True)
                except ValueError:
                    raise ValueError(f"Network filter {x} is invalid")

    def to_network_defs(self, server: "VpnServer") -> List[NetworkDef]:
        if self.server_group:
            return [self.server_group.resolve_subnet().cidr]
        if self.server_member:
            devices = self.server_member.device_set.all()
            return [ipaddress.ip_network(str(x.ip_address)) for x in devices]
        if self.subnet:
            return [self.subnet.cidr]
        if self.custom:
            return [self.parse_custom(server)]
        return [NetVar.Server]

    def _get_repr(self):
        if self.server_group:
            return "Group({})".format(self.server_group)
        if self.server_member:
            kind = self.server_member.member.get_real_instance()._meta.verbose_name.capitalize()  # noqa
            return f"{kind}({self.server_member.member})"
        if self.subnet:
            return str(self.subnet)
        if self.custom:
            return self.custom
        return "<default>"


class VpnFirewallRule(core_models.BaseFirewallRule):
    class Meta:
        verbose_name = _("Server Firewall Rule")

    server = models.ForeignKey("VpnServer", null=False, blank=False, on_delete=models.CASCADE)
    network_from = models.OneToOneField(
        VpnNetworkFilter,
        null=True,
        blank=True,
        on_delete=models.RESTRICT,
        related_name="network_from",
        verbose_name=_("From"),
    )
    network_to = models.ForeignKey(
        VpnNetworkFilter,
        null=True,
        blank=True,
        on_delete=models.RESTRICT,
        related_name="network_to",
        verbose_name=_("To"),
    )

    def __str__(self):
        return f"Rule {self.pk}"

    def _get_repr(self):
        return (
            f"{self.action} Service: {self.service or '<server>'} "
            f"From: {self.network_from or '<server-net>'} To: {self.network_to or '<server-net>'}"
        )

    def get_network_to_def(self, server: "VpnServer" = None) -> List[NetworkDef]:
        assert server is not None, "server should be passed as the context"
        if self.network_to:
            return self.network_to.to_network_defs(server)
        return [NetVar.Server]

    def get_network_from_def(self, server: "VpnServer" = None) -> List[NetworkDef]:
        assert server is not None, "server should be passed as the context"
        if self.network_from:
            return self.network_from.to_network_defs(server)
        return [NetVar.Server]


class ServerRule(WithComment, ServerRelated):
    class Meta(ServerRelated.Meta):
        abstract = True


class ServerRoutingRule(BaseRoutingRule, ServerRule):
    def resolved_interface_name(self, server: "VpnServer") -> Optional[str]:
        if self.interface is not None and self.interface.strip().lower() == "$self":
            return server.interface_name
        else:
            return self.interface


class ClientRule(WithComment, ServerRelated):
    class Meta(ServerRelated.Meta):
        abstract = True


class ClientRoutingRule(ClientRule):
    network = models.ForeignKey(core_models.Subnet, null=False, blank=False, on_delete=models.CASCADE)


class Device(NameableIdentifiable, WithComment, polymorphic_models.PolymorphicModel):
    class Meta:
        indexes = (GistIndex(fields=("ip_address",), opclasses=("inet_ops",), name="hidl_device_ipaddress_idx"),)

    server_to_member = models.ForeignKey("ServerToMember", on_delete=models.CASCADE, null=False, blank=True)
    ip_address = netfields.InetAddressField(null=False, blank=True, unique=True)
    mac_address = netfields.MACAddressField(null=True, blank=True)

    @classmethod
    @transaction.atomic
    def create_device_for_host(cls, host: core_models.Host, server: "VpnServer") -> "Device":
        server_to_member = ServerToMember.get_or_create(server=server, member=host)
        ip = server.service_factory.ip_allocation_service.allocate_ip(server_to_member.server, server_to_member.member)
        device = server.get_device_model().create_default(server_to_member=server_to_member, ip_address=ip)
        return device

    @classmethod
    def create_default(cls, server_to_member: "ServerToMember", ip_address: IpAddress) -> "Device":
        raise NotImplementedError

    @classmethod
    def generate_name(cls, server: "VpnServer", member: core_models.Member) -> str:
        return slugify("-".join((member.get_real_instance().get_name(), server.slug)))

    @staticmethod
    def get_devices_for_user(user: DjangoUser) -> List["Device"]:
        try:
            person = core_models.Person.objects.get(user__pk=user.pk)
            return Device.objects.filter(server_to_member__member=person).select_related("server_to_member__server")
        except core_models.Person.DoesNotExist:
            return []

    def generate_config(self) -> DeviceConfig:
        raise NotImplementedError

    def get_client_routing_rules(self) -> QuerySet["ClientRoutingRule"]:
        return ClientRoutingRule.load_related_to_servermember(self.server_to_member)

    def __str__(self) -> str:
        return f"{self.name}"


class ServerToMember(models.Model):
    class Meta:
        verbose_name = _("Server Member")
        verbose_name_plural = _("Server Members")
        unique_together = [("server", "member")]

    server = models.ForeignKey("VpnServer", on_delete=models.CASCADE)
    member = models.ForeignKey(core_models.Member, on_delete=models.RESTRICT)
    subnet = models.ForeignKey(core_models.Subnet, on_delete=models.RESTRICT, null=True, blank=True)

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None) -> None:
        super().save(force_insert, force_update, using, update_fields)
        if self.member.get_real_instance_class() == core_models.Host:
            Device.create_device_for_host(self.member.get_real_instance(), self.server)

    @classmethod
    def is_valid_member(cls, server: "VpnServer", member: core_models.Member) -> bool:
        if ServerToMember.objects.filter(server=server, member=member).exists():
            return True
        if server.servertogroup_set.filter(group=member.group).exists():
            return True
        return False

    @classmethod
    def get_or_create(cls, server: "VpnServer", member: core_models.Member) -> "ServerToMember":
        if cls.is_valid_member(server, member):
            return cls.objects.get_or_create(server=server, member=member)[0]
        raise PermissionDenied("{} is not allowed at server {}".format(member, server.name))

    def get_applicable_subnet(self) -> core_models.Subnet:
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


class VpnServer(NameableIdentifiable, WithComment, polymorphic_models.PolymorphicModel):
    class Meta:
        verbose_name = _("VPN Server")
        verbose_name_plural = _("VPN Servers")

    interface_name = models.CharField(max_length=16)
    ip_address = netfields.InetAddressField(null=False, blank=False)
    subnet = models.ForeignKey(core_models.Subnet, on_delete=models.RESTRICT)
    desired_state_raw = models.PositiveSmallIntegerField(
        null=False, blank=False, default=ServerState.STOPPED.value, db_column="desired_state"
    )
    state_change_job_id = models.CharField(max_length=100, null=True, blank=True)
    state_change_job_msg = models.CharField(max_length=100, null=True, blank=True)
    state_change_job_logs = models.TextField(null=True, blank=True)
    state_change_job_start = models.DateTimeField(null=True, blank=True)
    changes_made_ts = models.DateTimeField(null=True, blank=True)

    @cached_property
    def status(self) -> ServerStatus:
        return self.vpn_service.get_server_status(self)

    @property
    def is_running(self) -> bool:
        return self.status.state == ServerState.RUNNING

    @property
    def has_pending_changes(self) -> bool:
        if not self.is_running:
            return False
        return self.changes_made_ts is not None and self.changes_made_ts > self.state_change_job_start

    @property
    def desired_state(self) -> Optional[ServerState]:
        if self.desired_state_raw is None:
            return None
        return ServerState(self.desired_state_raw)

    @desired_state.setter
    def desired_state(self, val: Optional[ServerState]):
        self.desired_state_raw = str(val.value) if val is not None else None

    def register_state_change_message(self, msg: str, log: str = None):
        trimmed_message = msg
        trim_suffix = "..."
        max_len = self.__class__.state_change_job_msg.field.max_length
        if len(msg) > max_len:
            trimmed_message = msg[: max_len - len(trim_suffix)] + trim_suffix
        self.state_change_job_msg = trimmed_message
        self.state_change_job_logs = log
        self.save()

    def __str__(self):
        return f"{self.name}"

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

        # Create server routing rule if the admin has not created it themselves manually
        if is_creating and self.serverroutingrule_set.all().count() == 0:
            default_server_route = ServerRoutingRule.objects.create(
                server=self,
                network=self.subnet,
                interface="$self",
                comment=_("Default routing rule for server: send all related subnet to VPN interface "),
            )
            self.serverroutingrule_set.add(default_server_route)

    def get_or_create_member(self, member: "core_models.Member") -> "ServerToMember":
        return ServerToMember.get_or_create(self, member)

    def allocate_ip_for_member(self, member: "core_models.Member") -> str:
        self.service_factory.ip_allocation_service.allocate_ip(self, member)

    def get_ip_allocation_meta(self, subnet: core_models.Subnet) -> "IpAllocationMeta":
        return IpAllocationMeta.objects.get_or_create(server=self, subnet=subnet)[0]

    @classmethod
    def get_device_model(cls) -> Type["Device"]:
        raise NotImplementedError

    @staticmethod
    def get_servers_for_user(user: DjangoUser) -> List["VpnServer"]:
        try:
            person = core_models.Person.objects.get(user__pk=user.pk)
            return VpnServer.objects.filter(servertomember__member=person)
        except core_models.Person.DoesNotExist:
            return []

    @property
    def service_factory(self) -> VPNServiceFactory:
        return default_vpn_service_factory

    @property
    def vpn_service(self) -> "VPNService":
        raise NotImplementedError

    def stop(self, force=False) -> PostedJob:
        if not force and self.status.state == ServerState.STOPPED:
            raise ValueError(f"Server {self} is already stopped")
        if self.status.state.is_transitioning:
            raise ValueError(f"Server {self} is {self.status.state.label.lower()} now")
        self.desired_state = ServerState.STOPPED
        job = self.vpn_service.stop_vpn_server(self)
        self.state_change_job_id = job.uuid
        self.state_change_job_start = job.timestamp
        self.save()
        return job

    def start(self) -> PostedJob:
        if self.is_running:
            raise ValueError(f"Server {self} is already running")
        if self.status.state.is_transitioning:
            raise ValueError(f"Server {self} is {self.status.state.label.lower()} now")

        self.desired_state = ServerState.RUNNING
        job = self.vpn_service.start_vpn_server(self)
        self.state_change_job_id = job.uuid
        self.state_change_job_start = job.timestamp
        self.save()
        return job

    def register_transition_completed(self, job_result: JobResult):
        self.state_change_job_logs = str(job_result.result)
        self.save()

    def restart(self) -> PostedJob:
        return self.vpn_service.restart_vpn_server(self)

    def get_firewall_rules(self) -> QuerySet["VpnFirewallRule"]:
        return self.vpnfirewallrule_set.all()

    def get_routing_rules(self) -> QuerySet["ServerRoutingRule"]:
        return ServerRoutingRule.load_related_to_server(self).select_related("network")

    def get_admin_url(self):
        return reverse(
            "admin:%s_%s_change" % (VpnServer._meta.app_label, VpnServer._meta.model_name), args=(self.pk,)  # noqa
        )

    def get_devices(self) -> QuerySet["Device"]:
        return self.objects.filter(server_to_member__server=self)
