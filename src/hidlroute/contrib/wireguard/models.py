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

from typing import Type, Optional, Iterable, io

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from hidlroute.contrib.wireguard.service.key import generate_keypair, generate_private_key, generate_public_key
from hidlroute.contrib.wireguard.service.peer import generate_new_peer_config
from hidlroute.core import models as models_core
from hidlroute.core.models import DeviceConfig, SimpleTextDeviceConfig
from hidlroute.core.types import IpAddress


class WireGuardPeerConfig(SimpleTextDeviceConfig):
    pass


class WireguardPeer(models_core.Device):
    public_key = models.CharField(max_length=1024)

    @classmethod
    def create_default(cls, server_to_member: models_core.ServerToMember, ip_address: IpAddress) -> "WireguardPeer":
        private_key, public_key = generate_keypair()
        peer = WireguardPeer.objects.create(
            server_to_member=server_to_member, ip_address=ip_address, public_key=public_key
        )
        return peer

    def generate_config(self) -> DeviceConfig:
        private_key, public_key = generate_keypair()
        config_name = slugify(
            "-".join((self.server_to_member.member.get_real_instance().get_name(),
                      self.server_to_member.server.slug))) + ".conf"
        config = WireGuardPeerConfig(generate_new_peer_config(self, private_key), config_name)
        return config


class WireguardServer(models_core.Server):
    class Meta:
        verbose_name = _("Wireguard Server")

    private_key = models.CharField(max_length=1024, null=False, blank=False,
                                   default=generate_private_key)
    listen_port = models.IntegerField(null=False, default=5762)
    preshared_key = models.CharField(max_length=1024, blank=True, null=True)
    client_dns = models.CharField(max_length=1024, blank=True, null=True,
                                  help_text=_("DNS to be pushed to client configs"))
    client_keep_alive = models.IntegerField(blank=True, null=True,
                                            help_text=_("Keep alive options to be pushed to clients"))
    client_endpoint = models.CharField(max_length=1024, blank=False, null=False,
                                       help_text=_("Public server hostname or IP to be pushed to the client. \n"
                                                   "Optionally you could set port in a form of HOST:PORT to "
                                                   "override port for the client."))

    @classmethod
    def get_device_model(cls) -> Type[WireguardPeer]:
        return WireguardPeer

    def generate_public_key(self) -> str:
        if not self.private_key:
            raise ValueError("Private key must be set for server in order to generate public key")
        return generate_public_key(self.private_key)
