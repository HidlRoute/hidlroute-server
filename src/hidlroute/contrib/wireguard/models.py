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

from typing import Type, TYPE_CHECKING

from django.db import models
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from hidlroute.contrib.wireguard.factory import wireguard_service_factory, WireguardServiceFactory
from hidlroute.contrib.wireguard.service.key import generate_keypair, generate_private_key, generate_public_key
from hidlroute.contrib.wireguard.service.peer import generate_new_peer_config
from hidlroute.vpn import models as vpn_models
from hidlroute.core.types import IpAddress

if TYPE_CHECKING:
    from hidlroute.contrib.wireguard.service.wireguard_vpn import WireguardVPNService


class WireGuardPeerConfig(vpn_models.SimpleTextDeviceConfig):
    def __init__(self, content: str, name: str, public_key: str) -> None:
        super().__init__(content, name)
        self.public_key = public_key


class WireguardPeer(vpn_models.Device):
    public_key = models.CharField(max_length=1024)

    @classmethod
    def create_default(cls, server_to_member: vpn_models.ServerToMember, ip_address: IpAddress) -> "WireguardPeer":
        private_key, public_key = generate_keypair()
        peer = WireguardPeer.objects.create(
            name=cls.generate_name(server_to_member.server, server_to_member.member),
            server_to_member=server_to_member,
            ip_address=ip_address,
            public_key=public_key,
        )
        return peer

    def generate_config(self) -> vpn_models.DeviceConfig:
        private_key, public_key = generate_keypair()
        config_name = self.name + ".conf"
        config = WireGuardPeerConfig(generate_new_peer_config(self, private_key), config_name, public_key)
        return config


class WireguardServer(vpn_models.VpnServer):
    class Meta:
        verbose_name = _("Wireguard Server")

    _wireguard_vpn_service = None
    private_key = models.CharField(max_length=1024, null=False, blank=False, default=generate_private_key)
    listen_port = models.IntegerField(null=False, default=5762)
    preshared_key = models.CharField(max_length=1024, blank=True, null=True)
    client_dns = models.CharField(
        max_length=1024, blank=True, null=True, help_text=_("DNS to be pushed to client configs")
    )
    client_keep_alive = models.IntegerField(
        blank=True, null=True, help_text=_("Keep alive options to be pushed to clients")
    )
    client_endpoint = models.CharField(
        max_length=1024,
        blank=False,
        null=False,
        help_text=_(
            "Public server hostname or IP to be pushed to the client. \n"
            "Optionally you could set port in a form of HOST:PORT to "
            "override port for the client."
        ),
    )

    @property
    def service_factory(self) -> "WireguardServiceFactory":
        return wireguard_service_factory

    @property
    def vpn_service(self) -> "WireguardVPNService":
        return self.service_factory.wireguard_vpn_service

    @classmethod
    def get_device_model(cls) -> Type[WireguardPeer]:
        return WireguardPeer

    def generate_public_key(self) -> str:
        if not self.private_key:
            raise ValueError("Private key must be set for server in order to generate public key")
        return generate_public_key(self.private_key)

    def get_devices(self) -> QuerySet["WireguardPeer"]:
        return WireguardPeer.objects.filter(server_to_member__server=self)
