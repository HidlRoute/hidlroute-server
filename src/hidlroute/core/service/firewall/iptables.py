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

from enum import Enum
from typing import Optional, List

from hidlroute.core import models
from hidlroute.core.service.firewall.base import FirewallService, NativeFirewallRule, FirewallAction
from hidlroute.core.types import IpAddressOrNetwork
import iptc


class IpTablesFirewallAction(FirewallAction):
    RETURN = "RETURN"

    supported_actions = FirewallAction.supported_actions + [RETURN]


class IpTablesRule(NativeFirewallRule):
    def __init__(self, original_rule: Optional["models.FirewallRule"] = None) -> None:
        super().__init__(original_rule)
        self.source_port: Optional[int] = None
        self.protocol: Optional[str] = None
        self.dest_port: Optional[int] = None
        self.tcp_flags: Optional[List[str]] = None
        self.syn: Optional[bool] = None
        self.icmp_type: Optional[str] = None
        self.state: Optional[str] = None
        self.mac_src: Optional[str] = None
        self.log_prefix: Optional[str] = None
        self.scr_net: Optional[IpAddressOrNetwork] = None
        self.dst_net: Optional[IpAddressOrNetwork] = None
        self.action: Optional[str] = None

    @classmethod
    def to_port_str(cls, port_range: models.FirewallPortRange) -> str:
        s = str(port_range.start)
        if port_range.end:
            s += ":" + str(port_range.end)
        return s

    def set_protocol(self, port_range: models.FirewallPortRange):
        if port_range.protocol:
            # TODO: handle non standard e.g. PING
            self.protocol = port_range.protocol.lower()


class ChainType(Enum):
    INPUT = "in"
    OUTPUT = "out"
    FORWARD = "fw"


class IpTablesFirewallService(FirewallService):
    def build_native_firewall_rule(self, rule: "models.FirewallRule", server: "models.Server") -> List[IpTablesRule]:
        native_rules: List[IpTablesRule] = []
        self.ensure_rule_supported(rule)
        port_definitions: List[models.FirewallPortRange] = (
            rule.service.firewallportrange_set.all() if rule.service else [None]
        )
        for port_def in port_definitions:
            for from_net in rule.network_from.network_from or [None]:
                for to_net in rule.network_from.network_to or [None]:
                    native_rule = IpTablesRule(rule)
                    native_rule.action = rule.action.upper().strip()
                    native_rule.dest_port = native_rule.to_port_str(port_def)
                    native_rule.set_protocol(port_def)
                    if from_net is not None:
                        native_rule.scr_net = from_net
                    if to_net is not None:
                        native_rule.dst_net = to_net
                    native_rules.append(native_rule)
        return native_rules

    def _get_table_for_rule(self, rule: "models.FirewallRule") -> iptc.Table:
        # TODO: check action and return corresponding table for NAT and MANGLE
        return iptc.Table.FILTER

    def _get_chain_for_rule(self, rule: "models.FirewallRule", table: Optional[iptc.Table] = None) -> iptc.Chain:
        pass
        # if table is None:
        #     table = self._get_table_for_rule(rule)
        # from_net = rule.resolved_network_to(rule.server)
        # to_net = rule.resolved_network_to(rule.server)

    def _get_chain_name(self, chain_type: ChainType, server: "models.Server") -> str:
        return f"HIDL-{chain_type.value}-{server.slug}"

    def is_firewall_configured_for_server(self, server: "models.Server"):
        server_chains = [self._get_chain_name(x, server) for x in ChainType]
        for x in server_chains:
            if not iptc.easy.has_chain(iptc.Table.FILTER, x):
                return False
        # TODO: Check jump rules
        return True

    def install_chains(self, server: "models.Server"):
        # Input chain
        input_hidl_chain = self._get_chain_name(ChainType.INPUT, server)
        if not iptc.easy.has_chain(iptc.Table.FILTER, input_hidl_chain):
            iptc.easy.add_chain(iptc.Table.FILTER, input_hidl_chain)
        # Output chain
        output_hidl_chain = self._get_chain_name(ChainType.OUTPUT, server)
        if not iptc.easy.has_chain(iptc.Table.FILTER, output_hidl_chain):
            iptc.easy.add_chain(iptc.Table.FILTER, output_hidl_chain)
        # Input chain
        fwd_hidl_chain = self._get_chain_name(ChainType.FORWARD, server)
        if not iptc.easy.has_chain(iptc.Table.FILTER, fwd_hidl_chain):
            iptc.easy.add_chain(iptc.Table.FILTER, fwd_hidl_chain)

    def setup_firewall_for_server(self, server: "models.Server"):
        if not self.is_firewall_configured_for_server(server):
            self.install_chains(server)
        # default_routes = server.service_factory.networking_service.get_default_routes()
        # upstream_interfaces: List[NetInterface] = [x.interface for x in default_routes]
        # a = 1

    def destroy_firewall_for_server(self, server: "models.Server"):
        pass
