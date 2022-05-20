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
from typing import TYPE_CHECKING

from hidlroute.core.service.base import VPNService, VPNServerStatus

if TYPE_CHECKING:
    from hidlroute.core import models as core_models

LOGGER = logging.getLogger("hidl.contrib.dummy.service")


class DummyLoggingVPNService(VPNService):
    def start(self, server: "core_models.Server"):
        LOGGER.info(f"Started server {server}")

    def stop(self, server: "core_models.Server"):
        LOGGER.info(f"Stopped server {server}")

    def get_status(self, server: "core_models.Server") -> VPNServerStatus:
        LOGGER.info(f"Get server status: {server}")
        return VPNServerStatus.STOPPED
