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

# from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse, HttpRequest

from django.shortcuts import render

from hidlroute.vpn.models import VpnServer, Device


def device_list(request: HttpRequest):
    servers = VpnServer.get_servers_for_user(request.user)
    devices = Device.get_devices_for_user(request.user)
    context = {
        "servers_and_devices": [
            {"server": server, "devices": list(filter(lambda d: d.server_to_member.server_id == server.id, devices))}
            for server in servers
        ]
    }

    return render(request, "selfservice/device_list.html", context=context)


def device_add(request: HttpRequest):
    return HttpResponse("Device add")


def device_edit(request: HttpRequest, device_id: int):
    return HttpResponse("device_edit")
