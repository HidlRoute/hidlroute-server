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

from typing import Dict, List, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from hidlroute.contrib.wireguard import models


class CfgOpt:
    PrivateKey = "PrivateKey"
    PublicKey = "PublicKey"
    ListenPort = "ListenPort"
    Address = "Address"
    AllowedIPs = "AllowedIPs"
    PersistentKeepalive = "PersistentKeepalive"
    PresharedKey = "PresharedKey"
    DNS = "DNS"
    Endpoint = "Endpoint"


class CfgSection:
    Interface = "Interface"
    Peer = "Peer"


class WgConfigSection(object):
    def __init__(self, name: str) -> None:
        self.options: Dict[str, str] = dict()
        self.name = name

    def add(self, name: str, val: Any) -> "WgConfigSection":
        self.options[name] = str(val)
        return self

    def build(self) -> str:
        lines = [f"[{self.name}]"]
        for key, val in self.options.items():
            lines.append(f"{key} = {val}")
        return "\n".join(lines)


class WgConfigBuilder(object):
    def __init__(self) -> None:
        self.sections: List[WgConfigSection] = []

    def add_section(self, name: str) -> WgConfigSection:
        section = WgConfigSection(name)
        self.sections.append(section)
        return section

    def build(self) -> str:
        return "\n\n".join([x.build() for x in self.sections])


def generate_new_peer_config(peer: "models.WireguardPeer", private_key: str):
    builder = WgConfigBuilder()
    server: "models.WireguardServer" = peer.server_to_member.server.get_real_instance()

    # [Interface]
    interface_section = builder.add_section(CfgSection.Interface)
    interface_section.add(CfgOpt.PrivateKey, private_key)
    interface_section.add(CfgOpt.Address, peer.ip_address)
    if server.client_dns:
        interface_section.add(CfgOpt.DNS, server.client_dns)

    # [Peer]
    peer_section = builder.add_section(CfgSection.Peer)
    peer_section.add(CfgOpt.PublicKey, server.generate_public_key())
    endpoint = server.client_endpoint
    if ":" not in endpoint:
        endpoint += ":" + str(server.listen_port)
    peer_section.add(CfgOpt.Endpoint, endpoint)
    if server.preshared_key:
        peer_section.add(CfgOpt.PresharedKey, server.preshared_key)
    if server.client_keep_alive:
        peer_section.add(CfgOpt.PersistentKeepalive, server.client_keep_alive)
    allowed_ips = []
    for routing_rule in peer.get_client_routing_rules():
        allowed_ips.append(str(routing_rule.network.cidr))
    peer_section.add(CfgOpt.AllowedIPs, ", ".join(allowed_ips))
    return builder.build()
