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
    # TODO: Populate Allowed IPs here!

    return builder.build()
