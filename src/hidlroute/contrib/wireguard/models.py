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

from django.db import models
from django.utils.translation import gettext_lazy as _

from hidlroute.core import models as models_core


class WireguardServer(models_core.Server):
    class Meta:
        verbose_name = _("Wireguard Server")

    private_key = models.CharField(max_length=1024)
    listen_port = models.IntegerField(null=False, default=5762)


class WireguardPeer(models_core.Device):
    public_key = models.CharField(max_length=1024)
    preshared_key = models.CharField(max_length=1024, blank=True, null=True)
