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

from hidlroute.worker.management.celery_base import BaseCeleryCommand

LOGGER = logging.getLogger("hidl_core.service.worker.launcher")


class Command(BaseCeleryCommand):
    help = "Starts scheduler process"

    def handle(self, *args, **options):
        with self.workers_service.celery as celery:
            celery.start(("worker",) + args)
