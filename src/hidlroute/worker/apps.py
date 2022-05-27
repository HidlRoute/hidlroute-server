import importlib
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
