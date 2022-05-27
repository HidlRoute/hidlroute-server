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
import logging
from typing import List

import netfields
from django.conf import settings
from django.db import models

from django.utils.translation import gettext_lazy as _
from polymorphic import models as polymorphic_models
from treebeard import mp_tree

from hidlroute.core.base_models import NameableIdentifiable, WithComment, Sortable, WithReprCache
from hidlroute.core.types import NetworkDef

LOGGER = logging.getLogger("hidl_core.models")


class Subnet(NameableIdentifiable, WithComment, models.Model):
    cidr = netfields.CidrAddressField()

    def __str__(self) -> str:
        return f"{self.name} ({self.cidr})"


class Group(NameableIdentifiable, WithComment, mp_tree.MP_Node):
    DEFAULT_GROUP_SLUG = "x-default"

    def __str__(self):
        return f"{self.name}"

    @classmethod
    def get_default_group(cls):
        return cls.objects.get(slug=cls.DEFAULT_GROUP_SLUG)

    def get_full_name(self):
        return " / ".join([x.name for x in self.get_ancestors()] + [self.name])


class Member(WithComment, polymorphic_models.PolymorphicModel):
    group = models.ForeignKey(Group, on_delete=models.RESTRICT)

    def __str__(self) -> str:
        return str(self.get_real_instance())

    def get_name(self) -> str:
        raise NotImplementedError


class Person(Member):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=False, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.user.username} ({self.user.get_full_name()})"

    def get_name(self) -> str:
        return self.user.name


class Host(Member):
    host_name = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return f"H: {self.host_name}"

    def get_name(self) -> str:
        return self.host_name


class FirewallService(WithComment, NameableIdentifiable):
    pass


class FirewallPortRange(models.Model):
    protocol = models.CharField(max_length=20, null=True, blank=True)
    start = models.PositiveIntegerField(null=False, blank=False)
    end = models.PositiveIntegerField(null=True, blank=True)
    service = models.ForeignKey(FirewallService, on_delete=models.CASCADE)


class BaseRoutingRule(models.Model):
    class Meta:
        abstract = True

    network = models.ForeignKey(Subnet, null=True, blank=True, on_delete=models.CASCADE)
    gateway = netfields.InetAddressField(null=True, blank=True)
    interface = models.CharField(
        max_length=16,
        null=True,
        blank=True,
        help_text=_("Use special keyword $self to reference interface of the VPN server this route is attached to"),
    )

    def __str__(self) -> str:
        return f"{self.network.cidr} gw: {self.gateway or 'n/a'} iface: {self.interface or 'n/a'}"


class BaseFirewallRule(Sortable, WithComment, WithReprCache):
    class Meta:
        abstract = True

    action = models.CharField(max_length=20)
    service = models.ForeignKey(FirewallService, null=True, blank=True, on_delete=models.RESTRICT)

    @property
    def description(self) -> str:
        if self.comment:
            return self.comment
        if self.repr_cache:
            return self.repr_cache
        return str(self)

    @abc.abstractmethod
    def get_network_to_def(self, **ctx) -> List[NetworkDef]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_network_from_def(self, **ctx) -> List[NetworkDef]:
        raise NotImplementedError
