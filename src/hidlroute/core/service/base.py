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
from typing import NamedTuple, Any, Optional


class HidlNetworkingException(Exception):
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
    def prepare_for_serialization(self, obj: Any) -> Any:
        if hasattr("to_dict", obj):
            return obj.to_dict()
        else:
            return obj

    @abc.abstractmethod
    def get_job_result(self, job_uuid: str) -> JobResult:
        pass

    @abc.abstractmethod
    def wait_for_job(self, job_uuid: str, timeout: Optional[datetime.timedelta] = None) -> JobResult:
        pass

    @abc.abstractmethod
    def post_job(self, name: str, *args, **kwargs) -> PostedJob:
        pass
