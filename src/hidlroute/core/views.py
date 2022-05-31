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
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib import messages
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from django.shortcuts import render

from hidlroute.vpn import models as vpnmodels


class DeviceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["ip_address"].widget.attrs["readonly"] = True

        self.helper = FormHelper(self)
        self.helper.add_input(Submit("submit", _("Save Details")))

    class Meta:
        model = vpnmodels.Device
        fields = ["name", "ip_address"]

    def validate_unique(self):
        pass


def device_list(request: HttpRequest):
    servers = vpnmodels.VpnServer.get_servers_for_user(request.user)
    devices = vpnmodels.Device.get_devices_for_user(request.user)
    context = {
        "servers_and_devices": [
            {"server": server, "devices": list(filter(lambda d: d.server_to_member.server_id == server.id, devices))}
            for server in servers
        ]
    }

    return render(request, "selfservice/device_list.html", context=context)


def device_add(request: HttpRequest):
    device = vpnmodels.Device(name="New device")

    if request.method == "POST":
        form = DeviceForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect("/thanks/")
    else:
        form = DeviceForm(instance=device)

    return render(
        request,
        "selfservice/device_edit.html",
        {
            "form": form,
            "device": device,
        },
    )


def device_edit(request: HttpRequest, device_id: int):
    device = vpnmodels.Device.objects.get(pk=device_id)

    if request.method == "POST":
        form = DeviceForm(request.POST)
        if form.is_valid():
            try:
                device = form.save(commit=False)
                device.id = device_id
                device.save(update_fields=["name"])
                messages.add_message(request, messages.INFO, _("Saved device successfully."))
            except Exception as e:
                messages.add_message(request, messages.ERROR, _("Error saving device: %(error)s." % {"error": e}))
    else:
        form = DeviceForm(instance=device)

    return render(
        request,
        "selfservice/device_edit.html",
        {
            "form": form,
            "device": device,
        },
    )


def device_reveal_config(request, device_id: int) -> HttpResponse:
    device = vpnmodels.Device.objects.select_related("server_to_member__server").get(pk=device_id)
    server = device.server_to_member.server.get_real_instance()
    vpn_service = server.vpn_service
    return vpn_service.views.vpn_details_view(request, device)
