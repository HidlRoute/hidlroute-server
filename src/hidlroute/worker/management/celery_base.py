import argparse

import sys

from django.core.exceptions import ImproperlyConfigured
from django.core.management import BaseCommand, handle_default_options, CommandError
from django.core.management.base import SystemCheckError
from django.db import connections

from hidlroute.core.service.worker import CeleryWorkerService
from hidlroute.worker.utils import get_celery_worker_service


class BaseCeleryCommand(BaseCommand):
    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument("args", nargs=argparse.REMAINDER)

    def run_from_argv(self, argv):
        """
        Set up any environment changes requested (e.g., Python path
        and Django settings), then run this command. If the
        command raises a ``CommandError``, intercept it and print it sensibly
        to stderr. If the ``--traceback`` option is present or the raised
        ``Exception`` is not ``CommandError``, raise it.
        """
        self._called_from_command_line = True
        parser = self.create_parser(argv[0], argv[1])

        options, unknown = parser.parse_known_args(argv[2:])
        cmd_options = vars(options)
        # Move positional args out of options to mimic legacy optparse
        args = cmd_options.pop("args", ())
        handle_default_options(options)
        try:
            self.execute(*argv[2:], **cmd_options)
        except CommandError as e:
            if options.traceback:
                raise

            # SystemCheckError takes care of its own formatting.
            if isinstance(e, SystemCheckError):
                self.stderr.write(str(e), lambda x: x)
            else:
                self.stderr.write("%s: %s" % (e.__class__.__name__, e))
            sys.exit(e.returncode)
        finally:
            try:
                connections.close_all()
            except ImproperlyConfigured:
                # Ignore if connections aren't setup at this point (e.g. no
                # configured settings).
                pass

    @property
    def workers_service(self) -> CeleryWorkerService:
        return get_celery_worker_service()
