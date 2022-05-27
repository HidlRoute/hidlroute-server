from hidlroute.worker.management.celery_base import BaseCeleryCommand


class Command(BaseCeleryCommand):
    help = "Run arbitrary celery command"

    def handle(self, *args, **options):
        with self.workers_service.celery as celery:
            celery.do_vpn_server_start(args)
