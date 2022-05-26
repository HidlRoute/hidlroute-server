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

from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig

from easyaudit.apps import EasyAuditConfig


class EasyAuditApp(EasyAuditConfig):
    verbose_name = _("Security & Audit")


class WebConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hidlroute.web"
    label = "hidl_web"
    verbose_name = _("Hidl Route Web")

    def ready(self) -> None:
        super().ready()
