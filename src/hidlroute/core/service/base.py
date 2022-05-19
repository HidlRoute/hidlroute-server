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
import datetime
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from hidlroute.core import models


class VPNService(abc.ABC):
    def start(self, server: models.Server):
        pass

    def stop(self, server: models.Server):
        pass


class PostedJob(NamedTuple):
    uuid: str
    timestamp: datetime.datetime


class WorkerService(abc.ABC):
    def start_vpn_server(self, server: models.Server) -> PostedJob:
        pass

    def stop_vpn_server(self, server: models.Server) -> PostedJob:
        pass
