from hidlroute.core.factory import default_service_factory
from hidlroute.core.service.worker import CeleryWorkerService


def get_celery_worker_service() -> CeleryWorkerService:
    worker_service = default_service_factory.worker_service
    if isinstance(worker_service, CeleryWorkerService):
        return worker_service
    raise ValueError(
        "This command requires CeleryWorkerService implementation, "
        "but {} is currently registered".format(worker_service.__class__.__name__)
    )
