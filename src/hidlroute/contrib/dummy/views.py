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

from django.utils.functional import cached_property
from django.views.generic import TemplateView

from hidlroute.contrib.dummy.models import DummyDevice
from hidlroute.vpn.models import Device
from hidlroute.vpn.views import (
    BaseVPNDeviceConfigView,
    VPNServiceViews,
    DefaultVPNDeviceEditView,
    DefaultVPNDeviceAddView,
)


class DummyVPNConfigView(TemplateView, BaseVPNDeviceConfigView):
    def __init__(self, *args, **kwargs):
        super().__init__(template_name="hidl_dummy/config_view.html", *args, **kwargs)

    def post(self, request, device):
        return self.get(request, device=device)


class DummyVPNAddView(DefaultVPNDeviceAddView):
    def create_device_instance(self, server_to_member, **kwargs) -> Device:
        return DummyDevice.create_default(
            server_to_member, server_to_member.server.allocate_ip_for_member(server_to_member.member), kwargs["name"]
        )


class DummyVPNViews(VPNServiceViews):
    @cached_property
    def vpn_details_view(self):
        return DummyVPNConfigView.as_view()

    @cached_property
    def vpn_device_add_view(self) -> DefaultVPNDeviceEditView:
        return DummyVPNAddView.as_view()
