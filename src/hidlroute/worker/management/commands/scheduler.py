import argparse
import logging

from hidlroute.worker.management.celery_base import BaseCeleryCommand

LOGGER = logging.getLogger("hidl_core.service.worker.launcher")


class Command(BaseCeleryCommand):
    help = "Starts scheduler process"

    def add_arguments(self, parser: argparse.ArgumentParser):
        pass

    def handle(self, *args, **options):
        with self.workers_service.celery as celery:
            celery.start(("beat",))
