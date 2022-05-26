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

from hidlroute.contrib.dummy import models
from hidlroute.vpn.admin import DeviceAdmin, ServerAdmin


@DeviceAdmin.register_implementation(models.DummyDevice)
class DummyDeviceAdmin(DeviceAdmin.Impl):
    base_model = models.DummyDevice
    verbose_name = _("Dummy Device")


@ServerAdmin.register_implementation(models.DummyVpnServer)
class DummyServerAdmin(ServerAdmin.Impl):
    ICON = "images/server/logging.png"
    base_model = models.DummyVpnServer
    verbose_name = _("Dummy Server Config")
    verbose_name_plural = verbose_name

    fieldsets = ServerAdmin.Impl.fieldsets
