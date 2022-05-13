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

# from django.db import models

# Create your models here.
from django.db import models

from hidlroute.core.models import Server, Device


class WireguardServer(models.Model):
    server = models.OneToOneField(Server, on_delete=models.RESTRICT)
    private_key = models.CharField(max_length=1024)


class WireguardPeer(models.Model):
    device = models.ForeignKey(Device, on_delete=models.RESTRICT)
    public_key = models.CharField(max_length=1024)
