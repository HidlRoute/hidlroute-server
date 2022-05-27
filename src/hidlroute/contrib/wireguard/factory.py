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
from hidlroute.vpn.factory import VPNServiceFactory, default_vpn_service_factory

if TYPE_CHECKING:
    from hidlroute.contrib.wireguard.service.wireguard_vpn import WireguardVPNService


class WireguardServiceFactory(VPNServiceFactory):
    @cached_service
    def wireguard_vpn_service(self) -> "WireguardVPNService":
        return self._instance_from_str("hidlroute.contrib.wireguard.service.wireguard_vpn.WireguardVPNService")


wireguard_service_factory = WireguardServiceFactory(default_vpn_service_factory)
