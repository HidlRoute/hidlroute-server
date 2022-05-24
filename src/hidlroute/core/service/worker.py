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
from typing import Any, NamedTuple

from hidlroute.core import models
from hidlroute.core.service.base import WorkerService, ServerStateEnum, PostedJob


class SynchronousWorkerService(WorkerService):
    class JobRegistryItem(NamedTuple):
        posted_job: PostedJob
        result: Any

    def __init__(self) -> None:
        self.__job_registry = {}

    def __register_job_result(self, result: Any) -> PostedJob:
        _result = json.loads(json.dumps(result))
        new_uuid = uuid.uuid4().hex
        job = PostedJob(new_uuid, datetime.datetime.now())
        self.__job_registry[new_uuid] = self.JobRegistryItem(job, _result)
        return job

    def get_server_status(self, server: models.Server) -> ServerStateEnum:
        return server.vpn_service.get_status(server)

    def start_vpn_server(self, server: "models.Server") -> PostedJob:
        return self.__register_job_result(server.vpn_service.start(server))

    def stop_vpn_server(self, server: "models.Server") -> PostedJob:
        return self.__register_job_result(server.vpn_service.stop(server))

    def restart_vpn_server(self, server: "models.Server") -> PostedJob:
        return self.__register_job_result(server.vpn_service.restart(server))
