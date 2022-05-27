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

from django.apps import AppConfig

from django.utils.translation import gettext_lazy as _

from hidlroute.worker.utils import get_celery_worker_service

LOGGER = logging.getLogger("hidl_worker")


class WorkerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hidlroute.worker"
    label = "hidl_worker"
    verbose_name = _("Workers")

    def ready(self) -> None:
        super().ready()
        service = get_celery_worker_service()
        LOGGER.info("Discovering celery tasks")
        service.celery.autodiscover_tasks(related_name="jobs")
