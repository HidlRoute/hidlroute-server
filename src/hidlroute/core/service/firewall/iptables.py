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

from typing import Optional, List

from hidlroute.core import models
from hidlroute.core.service.firewall.base import FirewallService, NativeFirewallRule, FirewallAction
from hidlroute.core.types import IpAddressOrNetwork


class IpTablesFirewallAction(FirewallAction):
    JUMP = "JUMP"

    supported_actions = FirewallAction.supported_actions + [JUMP]


class IpTablesRule(NativeFirewallRule):
    def __init__(self, original_rule: Optional["models.ServerFirewallRule"] = None) -> None:
        super().__init__(original_rule)
        self.source_port: Optional[int] = None
        self.source_protocol: Optional[str] = None
        self.dest_port: Optional[int] = None
        self.dest_protocol: Optional[str] = None
        self.scr_net: Optional[IpAddressOrNetwork] = None
        self.dst_net: Optional[IpAddressOrNetwork] = None
        self.action: Optional[str] = None


class IpTablesFirewallService(FirewallService):
    def build_native_firewall_rule(
        self, rule: "models.ServerFirewallRule", server: "models.Server"
    ) -> List[IpTablesRule]:
        native_rule = IpTablesRule(rule)
        if IpTablesFirewallAction.if_action_supported(rule.action):
            native_rule.action = rule.action.upper().strip()
        else:
            raise ValueError(f"Invalid firewall rule {rule}: Action {rule.action} is not supported by iptables")

        return [native_rule]

    def setup_firewall_for_server(self, server: "models.Server"):
        pass

    def destroy_firewall_for_server(self, server: "models.Server"):
        pass
