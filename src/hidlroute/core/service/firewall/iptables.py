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

import logging
from enum import Enum
from typing import Optional, List, Any, Dict

from hidlroute.core import models
from hidlroute.vpn import models as vpn_models
from hidlroute.core.service.firewall.base import FirewallService, NativeFirewallRule, FirewallAction
from hidlroute.core.service.networking.base import NetVar, NetworkContext, NetworkingService
from hidlroute.core.types import IpAddressOrNetwork, NetworkDef, IpNetwork
import iptc

from hidlroute.core.utils import is_ip_network

LOGGER = logging.getLogger("hidl_core.service.firewall.iptables")


class IpTablesFirewallAction(FirewallAction):
    RETURN = "RETURN"

    supported_actions = FirewallAction.supported_actions + [RETURN]


class IpTablesRule(NativeFirewallRule):
    def __init__(self, original_rule: Optional["models.BaseFirewallRule"] = None) -> None:
        super().__init__(original_rule)
        self.source_port: Optional[str] = None
        self.protocol: Optional[str] = None
        self.dest_port: Optional[str] = None
        self.tcp_flags: Optional[List[str]] = None
        self.syn: Optional[bool] = None
        self.icmp_type: Optional[str] = None
        self.state: Optional[str] = None
        self.mac_src: Optional[str] = None
        self.log_prefix: Optional[str] = None
        self.scr_net: Optional[IpAddressOrNetwork] = None
        self.dst_net: Optional[IpAddressOrNetwork] = None
        self.action: Optional[str] = None
        self.comment: str = ""

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
    def build_native_firewall_rule(
        self, rule: "models.BaseFirewallRule", server: "vpn_models.VpnServer", network_context: NetworkContext
    ) -> List[IpTablesRule]:
        networking_service: NetworkingService = server.service_factory.networking_service  # noqa
        native_rules: List[IpTablesRule] = []
        self.ensure_rule_supported(rule)
        port_definitions: List[models.FirewallPortRange] = (
            rule.service.firewallportrange_set.all() if rule.service else [None]
        )
        for port_def in port_definitions:
            for from_net in networking_service.resolve_subnets(
                rule.get_network_from_def(server=server), network_context
            ) or [NetVar.Any]:
                for to_net in networking_service.resolve_subnets(
                    rule.get_network_to_def(server=server), network_context
                ) or [NetVar.Any]:
                    native_rule = IpTablesRule(rule)
                    native_rule.action = rule.action.upper().strip()
                    native_rule.comment = rule.description
                    native_rule.dest_port = native_rule.to_port_str(port_def)
                    native_rule.set_protocol(port_def)
                    if is_ip_network(from_net):
                        native_rule.scr_net = from_net
                    if is_ip_network(to_net):
                        native_rule.dst_net = to_net
                    native_rules.append(native_rule)
        return native_rules

    def get_default_policy(self, chain_type: ChainType, server: "vpn_models.VpnServer") -> str:
        return "DROP"

    def _get_table_for_rule(self, rule: "models.BaseFirewallRule") -> iptc.Table:
        # TODO: check action and return corresponding table for NAT and MANGLE
        return iptc.Table(iptc.Table.FILTER)

    def __is_internal_net(self, nets: List[NetworkDef], server_networks: List[IpNetwork]) -> bool:
        if NetVar.Host in nets:
            return False
        if NetVar.Self in nets:
            return True
        for x in nets:
            if not is_ip_network(x):
                continue
            for s in server_networks:
                if x.subnet_of(s):
                    return True
        return False

    def _get_chains_for_filter_rule(
        self,
        rule: "models.BaseFirewallRule",
        network_context: NetworkContext,
        table: Optional[iptc.Table],
        context: Dict[str, Any],
    ) -> List[iptc.Chain]:
        assert table.name == iptc.Table.FILTER
        networking_service: NetworkingService = rule.server.service_factory.networking_service  # noqa
        result: List[iptc.Chain] = []
        server = context.get("server", None)
        if table is None:
            table = self._get_table_for_rule(rule)
        from_net = networking_service.resolve_subnets(rule.get_network_from_def(**context), network_context)
        to_net = networking_service.resolve_subnets(rule.get_network_to_def(**context), network_context)
        if any([network_context.belongs_to_host(x) for x in to_net]):
            result.append(iptc.Chain(table, self._get_chain_name(ChainType.INPUT, server)))
        if any([network_context.belongs_to_host(x) for x in from_net]):
            result.append(iptc.Chain(table, self._get_chain_name(ChainType.OUTPUT, server)))
        result.append(iptc.Chain(table, self._get_chain_name(ChainType.FORWARD, server)))
        if len(result) == 0:
            LOGGER.warning("Rule {} doesn't belong to any chain".format(rule.description))
        return result

    def _get_chain_name(self, chain_type: ChainType, server: "vpn_models.VpnServer" = None) -> str:
        if server:
            return f"HIDL-{chain_type.value}-{server.slug}"
        return f"HIDL-{chain_type.value}"

    def is_firewall_configured_for_server(self, server: "vpn_models.VpnServer"):
        server_chains = [self._get_chain_name(x, server) for x in ChainType]
        for x in server_chains:
            if not iptc.easy.has_chain(iptc.Table.FILTER, x):
                return False
        # TODO: Check jump rules
        return True

    def _get_rule_prefix(self, server: Optional["vpn_models.VpnServer"] = None) -> str:
        if server is not None:
            return f"HIDL({server.slug}):"
        else:  # No server means HOST rule
            return "HIDL_HOST:"

    def _create_hidl_comment_matcher(self, comment: str, rule: iptc.Rule, server: "vpn_models.VpnServer") -> iptc.Rule:
        m = rule.create_match("comment")
        m.comment = self._get_rule_prefix(server) + " " + comment
        rule.matches.append(m)
        return rule

    def _create_port_matcher(self, rule: iptc.Rule, native_rule: IpTablesRule) -> iptc.Rule:
        if (native_rule.source_port and ":" in native_rule.source_port) or (
            native_rule.dest_port and ":" in native_rule.dest_port
        ):
            port_matcher = rule.create_match("multiport")
            if native_rule.dest_port:
                port_matcher.dports = native_rule.dest_port
            if native_rule.source_port:
                port_matcher.sports = native_rule.source_port
        else:
            port_matcher = rule.create_match(native_rule.protocol)
            if native_rule.source_port:
                port_matcher.sport = native_rule.source_port
            if native_rule.dest_port:
                port_matcher.dport = native_rule.dest_port
        rule.matches.append(port_matcher)
        return rule

    def __find_hidl_rules_in_chain(self, chain: iptc.Chain, server: Optional["vpn_models.VpnServer"] = None):
        prefix = self._get_rule_prefix(server)
        result: List[iptc.Rule] = []
        for r in chain.rules:  # type: iptc.Rule
            for m in r.matches:
                if m.name == "comment" and m.parameters.get("comment", "").startswith(prefix):
                    result.append(r)
        return result

    def __uninstall_server_rules_for_chain(
        self, chain_name: str, server: "vpn_models.VpnServer", table: Optional[iptc.Table] = None
    ):
        if table is None:
            table = iptc.Table(iptc.Table.FILTER)
        chain = iptc.Chain(table, chain_name)
        rules = self.__find_hidl_rules_in_chain(chain, server)
        for r in rules:
            chain.delete_rule(r)

    def _uninstall_server_rules(self, server: "vpn_models.VpnServer"):
        table = iptc.Table(iptc.Table.FILTER)
        table.refresh()
        try:
            table.autocommit = False
            # Input chain
            self.__uninstall_server_rules_for_chain("INPUT", server, table)
            # Output
            self.__uninstall_server_rules_for_chain("OUTPUT", server, table)
            # Forward chain
            self.__uninstall_server_rules_for_chain("FORWARD", server, table)
            table.commit()
        finally:
            table.autocommit = True
            table.refresh()

    def _install_jump_rules(self, server: "vpn_models.VpnServer"):
        table = iptc.Table(iptc.Table.FILTER)
        table.autocommit = True
        chain = iptc.Chain(table, "INPUT")
        # Input chain
        rule = iptc.Rule()
        rule.target = rule.create_target(self._get_chain_name(ChainType.INPUT, server))
        self._create_hidl_comment_matcher("JUMP Jump rule for INPUT chain", rule, server)
        chain.append_rule(rule)
        # Output chain
        chain = iptc.Chain(table, "OUTPUT")
        rule = iptc.Rule()
        rule.target = rule.create_target(self._get_chain_name(ChainType.OUTPUT, server))
        self._create_hidl_comment_matcher("JUMP Jump rule for OUTPUT chain", rule, server)
        chain.append_rule(rule)
        chain.append_rule(rule)
        # Forward chain
        chain = iptc.Chain(table, "FORWARD")
        rule = iptc.Rule()
        rule.target = rule.create_target(self._get_chain_name(ChainType.FORWARD, server))
        self._create_hidl_comment_matcher("JUMP Jump rule for FORWARD chain (inbound traffic)", rule, server)
        chain.append_rule(rule)

    def _install_chains(self, server: "vpn_models.VpnServer"):
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

    def _create_default_rules(self, server: "vpn_models.VpnServer"):
        output_chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), self._get_chain_name(ChainType.OUTPUT, server))
        rule = iptc.Rule()
        match = rule.create_match("state")
        match.state = "RELATED,ESTABLISHED"
        rule.add_match(match)
        rule.target = iptc.Target(rule, "ACCEPT")
        self._create_hidl_comment_matcher("Allow established and related", rule, server)
        output_chain.append_rule(rule)

    def _uninstall_chains(self, server: "vpn_models.VpnServer"):
        self._uninstall_server_rules(server)
        server_chains = [self._get_chain_name(x, server) for x in ChainType]
        iptc.easy.batch_delete_chains(iptc.Table.FILTER, server_chains)

    def _clear_chain(self, chain_name):
        chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), chain_name)
        chain.flush()

    def _ensure_empty_chains(self, server: "vpn_models.VpnServer"):
        if not self.is_firewall_configured_for_server(server):
            self._install_chains(server)
        server_chains = [self._get_chain_name(x, server) for x in ChainType]
        for x in server_chains:
            self._clear_chain(x)

    def _ensure_jump_rules(self, server: "vpn_models.VpnServer"):
        self._uninstall_server_rules(server)
        self._install_jump_rules(server)

    def _append_native_rule(
        self, native_rule: IpTablesRule, chain: iptc.Chain, server: "vpn_models.VpnServer"
    ) -> iptc.Rule:
        rule = iptc.Rule()
        if native_rule.scr_net:
            rule.src = str(native_rule.scr_net)
        if native_rule.dst_net:
            rule.dst = str(native_rule.dst_net)
        if native_rule.protocol:
            rule.protocol = native_rule.protocol.lower()
        if native_rule.protocol.lower() in ("tcp", "udp") and (native_rule.dest_port or native_rule.source_port):
            self._create_port_matcher(rule, native_rule)
        # TODO: ICMP, States, mac, etc.
        rule.target = rule.create_target(native_rule.action)
        self._create_hidl_comment_matcher(native_rule.comment, rule, server)
        chain.append_rule(rule)
        return rule

    def _install_server_rules(self, server: "vpn_models.VpnServer"):
        self._create_default_rules(server)
        network_context = NetworkContext(
            server_ip=server.ip_address,
            server_networks=server.vpn_service.get_subnets_for_server(server),
            host_networks=server.vpn_service.get_non_server_networks(server),
        )
        context = dict(server=server)
        for rule in server.get_firewall_rules():
            native_rules = self.build_native_firewall_rule(rule, server, network_context)
            table = self._get_table_for_rule(rule)
            for nr in native_rules:
                if table.name == iptc.Table.FILTER:
                    chains = self._get_chains_for_filter_rule(rule, network_context, table, context)
                    for c in chains:
                        self._append_native_rule(nr, c, server)

    def setup_firewall_for_server(self, server: "vpn_models.VpnServer"):
        self._ensure_empty_chains(server)
        self._ensure_jump_rules(server)
        self._install_server_rules(server)

    def destroy_firewall_for_server(self, server: "vpn_models.VpnServer"):
        self._uninstall_server_rules(server)
        self._uninstall_chains(server)
