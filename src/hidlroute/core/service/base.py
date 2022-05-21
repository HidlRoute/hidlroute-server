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
from enum import Enum
from typing import NamedTuple, TYPE_CHECKING

from hidlroute.core.utils import django_enum

if TYPE_CHECKING:
    from hidlroute.core import models


@django_enum
class VPNServerStatus(Enum):
    STOPPED = 1
    RUNNING = 2
    STARTING = 3
    FAILE = 4
    RUNNING_CHANGES_PENDING = 5


class VPNService(abc.ABC):
    @abc.abstractmethod
    def start(self, server: "models.Server"):
        pass

    @abc.abstractmethod
    def stop(self, server: "models.Server"):
        pass

    def restart(self, server: "models.Server"):
        self.stop(server)
        self.start(server)

    @abc.abstractmethod
    def get_status(self, server: "models.Server") -> VPNServerStatus:
        raise NotImplementedError


class PostedJob(NamedTuple):
    uuid: str
    timestamp: datetime.datetime


class WorkerService(abc.ABC):
    @abc.abstractmethod
    def start_vpn_server(self, server: "models.Server") -> PostedJob:
        pass

    @abc.abstractmethod
    def stop_vpn_server(self, server: "models.Server") -> PostedJob:
        pass

    @abc.abstractmethod
    def restart_vpn_server(self, server: "models.Server") -> PostedJob:
        pass

    @abc.abstractmethod
    def get_server_status(self, server: "models.Server") -> VPNServerStatus:
        pass
