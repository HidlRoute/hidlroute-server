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
from typing import TYPE_CHECKING, List, Optional

from hidlroute.core.types import IpNetwork

if TYPE_CHECKING:
    from hidlroute.core import models
    from hidlroute.vpn import models as vpn_models


class FirewallAction(object):
    ACCEPT = "ACCEPT"
    DENY = "DENY"
    REJECT = "REJECT"
    LOG = "LOG"

    supported_actions = [ACCEPT, DENY, REJECT, LOG]


class FirewallProtocol(object):
    TCP = "TCP"
    UDP = "UDP"
    ICMP = "ICMP"
    GRE = "GRE"

    supported_protocols = [TCP, UDP, ICMP, GRE]


class NativeFirewallRule(abc.ABC):
    """Base class for native firewall rule"""

    def __init__(self, original_rule: Optional["models.BaseFirewallRule"] = None) -> None:
        self.original_rule = original_rule


class FirewallService(abc.ABC):
    def get_supported_actions(self) -> List[str]:
        return FirewallAction.supported_actions

    def if_action_supported(self, action: str) -> bool:
        if action is None:
            return False
        return action.strip().upper() in self.get_supported_actions()

    def get_supported_protocols(self) -> List[str]:
        return FirewallProtocol.supported_protocols

    def is_supported_protocol(self, protocol: str) -> bool:
        if protocol is None:
            return False
        return protocol.strip().upper() in self.get_supported_protocols()

    def ensure_rule_supported(self, rule: "models.BaseFirewallRule"):
        if not self.if_action_supported(rule.action):
            raise ValueError(f"Invalid firewall rule {rule}: Action {rule.action} is not supported by iptables")
        if rule.service:
            for port_def in rule.service.firewallportrange_set.all():
                if not self.is_supported_protocol(port_def.protocol):
                    raise ValueError(
                        f"Invalid firewall rule {rule}: " f"Protocol {rule.action} is not supported by iptables"
                    )

    def build_native_firewall_rule(
        self, rule: "models.BaseFirewallRule", server: "vpn_models.VpnServer", server_networks: List[IpNetwork]
    ) -> List[NativeFirewallRule]:
        return []

    @abc.abstractmethod
    def setup_firewall_for_server(self, server: "vpn_models.VpnServer"):
        pass

    @abc.abstractmethod
    def destroy_firewall_for_server(self, server: "vpn_models.VpnServer"):
        pass
