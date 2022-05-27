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
import logging
import uuid
from dataclasses import dataclass
from typing import Any, Optional, Dict

from celery import Celery
from celery.result import AsyncResult

from hidlroute.core.service.base import WorkerService, PostedJob, JobStatus, JobResult


class SynchronousWorkerService(WorkerService):
    @dataclass
    class JobRegistryItem:
        posted_job: PostedJob
        status: JobStatus
        result: Any

    def __init__(self) -> None:
        self.__job_registry: Dict[str, SynchronousWorkerService.JobRegistryItem] = {}

    def __register_new_job(self) -> PostedJob:
        new_uuid = uuid.uuid4().hex
        job = PostedJob(new_uuid, datetime.datetime.now())
        self.__job_registry[new_uuid] = self.JobRegistryItem(
            job,
            JobStatus.PENDING,
            None,
        )
        return job

    def __register_job_result(self, job_uuid: str, result: Any, exc: Optional[Exception] = None) -> JobResult:
        if job_uuid in self.__job_registry:
            record = self.__job_registry[job_uuid]
            record.status = JobStatus.SUCCESS if exc is None else JobStatus.FAILED
            _result = (
                json.loads(json.dumps(self.prepare_for_serialization(result))) if exc is None else dict(error=str(exc))
            )
            record.result = _result
            return JobResult(job_uuid, record.status, record.result, record.posted_job.timestamp)
        else:
            raise ValueError(f"Job {job_uuid} doesn't exist")

    def get_job_result(self, job_uuid: str, fail_if_not_exist=False) -> Optional[JobResult]:
        if job_uuid in self.__job_registry:
            record = self.__job_registry[job_uuid]
            return JobResult(job_uuid, record.status, record.result, record.posted_job.timestamp)
        if not fail_if_not_exist:
            return None
        raise ValueError(f"Job {job_uuid} doesn't exist")

    def wait_for_job(self, job_uuid: str, timeout: Optional[datetime.datetime] = None) -> JobResult:
        return self.get_job_result(job_uuid, True)

    def post_job(self, name: str, **params: Dict[str, Any]) -> PostedJob:
        posted_job = self.__register_new_job()
        return posted_job


class CeleryWorkerService(WorkerService):
    def __init__(self) -> None:
        super().__init__()
        self.celery = Celery("hidl")
        self.celery.config_from_object("django.conf:settings", namespace="CELERY")
        self.celery.log.setup(logging.root.level, redirect_stdouts=False)

        self.__celery_status_to_job_status = {
            "FAILURE": JobStatus.FAILED,
            "SUCCESS": JobStatus.SUCCESS,
            "PENDING": JobStatus.PENDING,
            "RETRY": JobStatus.FAILED,
        }

    def __celery_result_to_job_result(self, celery_result: AsyncResult) -> JobResult:
        return JobResult(
            celery_result.id,
            status=self.__celery_status_to_job_status[celery_result.status],
            timestamp=datetime.datetime.now(),
            result=celery_result.result,
        )

    def get_job_result(self, job_uuid: str) -> JobResult:
        res = AsyncResult(job_uuid)
        return self.__celery_result_to_job_result(res)

    def wait_for_job(self, job_uuid: str, timeout: Optional[datetime.timedelta] = None) -> JobResult:
        res = AsyncResult(job_uuid)
        res.wait(timeout.total_seconds(), interval=0.5)
        return self.__celery_result_to_job_result(res)

    def post_job(self, name: str, *args, **kwargs) -> PostedJob:
        ts = datetime.datetime.now()
        res: AsyncResult = self.celery.send_task(name, args, kwargs)
        return PostedJob(res.id, ts)
