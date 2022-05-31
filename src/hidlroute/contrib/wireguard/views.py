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

from django.shortcuts import render
from qrcode import QRCode
import base64

from hidlroute.vpn.views import BaseVPNDeviceConfigView


class WireguardDeviceVPNConfigView(BaseVPNDeviceConfigView):
    CLIENT_CONFIG_FILENAME = "wg0.conf"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def post(self, request, device):
        with BytesIO() as buffer:
            config = device.generate_config()

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
