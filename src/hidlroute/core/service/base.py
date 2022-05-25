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
from typing import NamedTuple, TYPE_CHECKING, Any, Optional
from django.utils.translation import gettext_lazy as _

from hidlroute.core.utils import django_enum

if TYPE_CHECKING:
    from hidlroute.core import models


@django_enum
class ServerState(Enum):
    STOPPED = 0x100
    RUNNING = 0x101
    FAILED = 0x102

    STOPPING = 0x200
    STARTING = 0x201
    UNKNOWN = 0xFFF  # Indicates inconsistent state

    __labels__ = {
        STOPPED: _("Stopped"),
        RUNNING: _("Running"),
        FAILED: _("Failed"),
        STOPPING: _("Stopping"),
        STARTING: _("Starting"),
        UNKNOWN: _("Unknown"),
    }

    @property
    def label(self) -> str:
        if self in ServerState.__labels__:
            return ServerState.__labels__[self]
        return self.name

    @property
    def is_running(self) -> bool:
        return self == self.RUNNING

    @property
    def is_transitioning(self) -> bool:
        return self in (self.STARTING, self.STOPPING)


class HidlNetworkingException(BaseException):
    pass


class ServerStatus:
    def __init__(self, state: ServerState) -> None:
        self.state = state


class VPNService(abc.ABC):
    @abc.abstractmethod
    def start(self, server: "models.VpnServer"):
        pass

    @abc.abstractmethod
    def stop(self, server: "models.VpnServer"):
        pass

    def restart(self, server: "models.VpnServer"):
        job = server.stop()
        server.service_factory.worker_service.wait_for_job(job.uuid)
        server = server.__class__.objects.get(pk=server.pk)  # Force reload from DB and new instance to clear all caches
        job = server.start()
        server.service_factory.worker_service.wait_for_job(job.uuid)

    @abc.abstractmethod
    def get_status(self, server: "models.VpnServer") -> ServerStatus:
        pass


class JobStatus(Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class PostedJob(NamedTuple):
    uuid: str
    timestamp: datetime.datetime


class JobResult(NamedTuple):
    uuid: str
    status: JobStatus
    result: Any = None
    timestamp: datetime.datetime = None


class WorkerService(abc.ABC):
    @abc.abstractmethod
    def start_vpn_server(self, server: "models.VpnServer") -> PostedJob:
        pass

    @abc.abstractmethod
    def stop_vpn_server(self, server: "models.VpnServer") -> PostedJob:
        pass

    @abc.abstractmethod
    def restart_vpn_server(self, server: "models.VpnServer") -> PostedJob:
        pass

    @abc.abstractmethod
    def get_server_status(self, server: "models.VpnServer") -> ServerState:
        pass

    @abc.abstractmethod
    def get_job_result(self, job_uuid: str) -> JobResult:
        pass

    @abc.abstractmethod
    def wait_for_job(self, job_uuid: str, timeout: Optional[datetime.datetime] = None) -> JobResult:
        pass
