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

import datetime
import json
import uuid
from typing import Any, NamedTuple, Optional, Dict

from hidlroute.core import models
from hidlroute.core.service.base import WorkerService, PostedJob, ServerStatus, JobStatus, JobResult


class SynchronousWorkerService(WorkerService):
    class JobRegistryItem(NamedTuple):
        posted_job: PostedJob
        status: JobStatus
        result: Any

    def __init__(self) -> None:
        self.__job_registry: Dict[str, SynchronousWorkerService.JobRegistryItem] = {}

    def __register_job_result(self, result: Any, exc: Optional[Exception] = None) -> PostedJob:
        _result = json.loads(json.dumps(result)) if exc is None else dict(error=str(exc))
        new_uuid = uuid.uuid4().hex
        job = PostedJob(new_uuid, datetime.datetime.now())
        self.__job_registry[new_uuid] = self.JobRegistryItem(
            job,
            JobStatus.SUCCESS if exc is None else JobStatus.FAILED,
            _result,
        )
        return job

    def get_server_status(self, server: models.Server) -> ServerStatus:
        return server.vpn_service.get_status(server)

    def start_vpn_server(self, server: "models.Server") -> PostedJob:
        try:
            return self.__register_job_result(server.vpn_service.start(server))
        except Exception as e:
            return self.__register_job_result(None, e)

    def stop_vpn_server(self, server: "models.Server") -> PostedJob:
        try:
            return self.__register_job_result(server.vpn_service.stop(server))
        except Exception as e:
            return self.__register_job_result(None, e)

    def restart_vpn_server(self, server: "models.Server") -> PostedJob:
        try:
            self.__register_job_result(server.vpn_service.restart(server))
        except Exception as e:
            return self.__register_job_result(None, e)

    def get_job_result(self, job_uuid: str, fail_if_not_exist=False) -> Optional[JobResult]:
        if job_uuid in self.__job_registry:
            record = self.__job_registry[job_uuid]
            return JobResult(job_uuid, record.status, record.result, record.posted_job.timestamp)
        if not fail_if_not_exist:
            return None
        raise ValueError(f"Job {job_uuid} doesn't exist")

    def wait_for_job(self, job_uuid: str, timeout: Optional[datetime.datetime] = None) -> JobResult:
        return self.get_job_result(job_uuid, True)
