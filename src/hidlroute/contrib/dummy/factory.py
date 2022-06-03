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

from typing import TYPE_CHECKING

from hidlroute.core.factory import cached_service

from hidlroute.core.service.firewall.base import FirewallService
from hidlroute.core.service.networking.base import NetworkingService
from hidlroute.vpn.factory import VPNServiceFactory, default_vpn_service_factory

if TYPE_CHECKING:
    from hidlroute.contrib.dummy.service.vpn import DummyLoggingVPNService


class DummyServiceFactory(VPNServiceFactory):
    @cached_service
    def networking_service(self) -> NetworkingService:
        return self._instance_from_str("hidlroute.contrib.dummy.service.network.DummyNetworkingService")

    @cached_service
    def firewall_service(self) -> FirewallService:
        return self._instance_from_str("hidlroute.contrib.dummy.service.network.DummyFirewallService")

    @cached_service
    def dummy_vpn_service(self) -> "DummyLoggingVPNService":
        return self._instance_from_str("hidlroute.contrib.dummy.service.vpn.DummyLoggingVPNService")


dummy_service_factory = DummyServiceFactory(default_vpn_service_factory)
