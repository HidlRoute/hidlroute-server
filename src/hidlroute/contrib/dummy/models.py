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

from typing import Type

from django.utils.translation import gettext_lazy as _

from hidlroute.contrib.dummy.dummy_factory import dummy_service_factory
from hidlroute.contrib.dummy.service.vpn import DummyLoggingVPNService
from hidlroute.core import models as models_core
from hidlroute.core.factory import ServiceFactory
from hidlroute.core.service.base import VPNService
from hidlroute.core.types import IpAddress

_dummy_logging_VPN_service = DummyLoggingVPNService()


class DummyDevice(models_core.Device):
    @classmethod
    def create_default(cls, server_to_member: models_core.ServerToMember, ip_address: IpAddress) -> "DummyDevice":
        peer = cls.objects.create(
            name=cls.generate_name(server_to_member.server, server_to_member.member),
            server_to_member=server_to_member,
            ip_address=ip_address,
        )
        return peer


class DummyServer(models_core.Server):
    class Meta:
        verbose_name = _("Dummy Server")

    @classmethod
    def get_device_model(cls) -> Type[DummyDevice]:
        return DummyDevice

    @property
    def service_factory(self) -> ServiceFactory:
        return dummy_service_factory

    @property
    def vpn_service(self) -> VPNService:
        return _dummy_logging_VPN_service
