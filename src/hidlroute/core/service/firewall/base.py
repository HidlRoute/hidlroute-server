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

if TYPE_CHECKING:
    from hidlroute.core import models


class FirewallAction(object):
    ACCEPT = "ACCEPT"
    DENY = "DENY"
    REJECT = "REJECT"
    LOG = "LOG"

    supported_actions = [ACCEPT, DENY, REJECT, LOG]

    @classmethod
    def if_action_supported(cls, action: str) -> bool:
        if action is None:
            return False
        return action.strip().upper() in cls.supported_actions


class FirewallProtocol(object):
    TCP = "TCP"
    UDP = "UDP"
    ICMP = "ICMP"
    GRE = "GRE"

    supported_protocols = [TCP, UDP, ICMP, GRE]

    @classmethod
    def if_protocol_supported(cls, protocol: str) -> bool:
        if protocol is None:
            return False
        return protocol.strip().upper() in cls.supported_protocols


class NativeFirewallRule(abc.ABC):
    """Base class for native firewall rule"""

    def __init__(self, original_rule: Optional["models.ServerFirewallRule"] = None) -> None:
        self.original_rule = original_rule


class FirewallService(abc.ABC):
    def get_supported_actions(self) -> List[str]:
        return FirewallAction.supported_actions

    def get_supported_protocols(self) -> List[str]:
        return FirewallProtocol.supported_protocols

    def build_native_firewall_rule(
        self, rule: "models.ServerFirewallRule", server: "models.Server"
    ) -> List[NativeFirewallRule]:
        return []

    @abc.abstractmethod
    def setup_firewall_for_server(self, server: "models.Server"):
        pass

    @abc.abstractmethod
    def destroy_firewall_for_server(self, server: "models.Server"):
        pass
