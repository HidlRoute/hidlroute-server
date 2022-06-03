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

from io import BytesIO

from django.utils.translation import gettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.shortcuts import render
from django.utils.functional import cached_property
from qrcode import QRCode
import base64

from hidlroute.contrib.wireguard.models import WireguardPeer, WireGuardPeerConfig
from hidlroute.vpn.models import Device
from hidlroute.vpn.views import (
    BaseVPNDeviceConfigView,
    DefaultVPNDeviceEditView,
    VPNServiceViews,
    DefaultVPNDeviceAddView,
    DeviceEditForm,
)


class WireguardPeerEditForm(DeviceEditForm):
    ALLOW_EDIT_FIELDS = ("name",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = WireguardPeer
        fields = ["name", "ip_address"]

    def validate_unique(self):
        pass


class WireguardPeerAddForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit("submit", _("Save Details")))

    class Meta:
        model = WireguardPeer
        fields = ["name"]


class WireguardVPNDeviceEditView(DefaultVPNDeviceEditView):
    _FORM_CLASS = WireguardPeerEditForm


class WireguardVPNDeviceAddView(DefaultVPNDeviceAddView):
    _FORM_CLASS = WireguardPeerAddForm

    def create_device_instance(self, server_to_member, **kwargs) -> Device:
        return WireguardPeer.create_default(
            server_to_member, server_to_member.server.allocate_ip_for_member(server_to_member.member), kwargs["name"]
        )


class WireguardVPNViews(VPNServiceViews):
    @cached_property
    def vpn_details_view(self):
        return WireguardDeviceVPNConfigView.as_view()

    @cached_property
    def vpn_device_edit_view(self) -> DefaultVPNDeviceEditView:
        return WireguardVPNDeviceEditView.as_view()

    @cached_property
    def vpn_device_add_view(self) -> DefaultVPNDeviceEditView:
        return WireguardVPNDeviceAddView.as_view()


class WireguardDeviceVPNConfigView(BaseVPNDeviceConfigView):
    CLIENT_CONFIG_FILENAME = "wg0.conf"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def post(self, request, device):
        with BytesIO() as buffer:
            config: WireGuardPeerConfig = device.generate_config()
            device.update_fields(public_key=config.public_key)

            qrcode = QRCode()
            qrcode.add_data(config.as_str())
            image = qrcode.make_image()
            image.save(buffer, format="png")
            config_qr_base64 = base64.b64encode(buffer.getbuffer()).decode("utf-8")
            return render(
                request,
                "hidl_wg/config_view.html",
                {
                    "device": device,
                    "config": config,
                    "config_qr_base64": config_qr_base64,
                    "client_config_filename": WireguardDeviceVPNConfigView.CLIENT_CONFIG_FILENAME,
                },
            )
