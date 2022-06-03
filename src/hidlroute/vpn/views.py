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

import abc
from functools import cached_property

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from hidlroute.core import models as coremodels
from django import forms

from hidlroute.core.models import Person
from hidlroute.vpn.models import ServerToMember, Device
from django.http import HttpResponse, HttpRequest
from hidlroute.vpn import models as vpnmodels


def device_add(request: HttpRequest, server_id: int):
    server = vpnmodels.VpnServer.objects.get(pk=server_id).get_real_instance()
    vpn_service = server.vpn_service
    return vpn_service.views.vpn_device_add_view(request, server=server)


def device_edit(request: HttpRequest, device_id: int):
    device = vpnmodels.Device.objects.select_related("server_to_member__server").get(pk=device_id)
    server = device.server_to_member.server.get_real_instance()
    vpn_service = server.vpn_service
    return vpn_service.views.vpn_device_edit_view(request, device=device)


def device_reveal_config(request, device_id: int) -> HttpResponse:
    device = vpnmodels.Device.objects.select_related("server_to_member__server").get(pk=device_id)
    server = device.server_to_member.server.get_real_instance()
    vpn_service = server.vpn_service
    return vpn_service.views.vpn_details_view(request, device=device)


class OwnDeviceCheckMixin(AccessMixin):
    """
    Checks that device which is being edited belongs to the user who edits it.
    """

    def dispatch(self, request, *args, **kwargs):
        device = kwargs.get("device", None)
        server = kwargs.get("server", None)
        if device is None and server is None:
            raise ValueError("For controlled access mixin there should be wither device or server kwarg.")
        if device:
            member = device.server_to_member.member.get_real_instance()
            if not isinstance(member, Person):
                return self.handle_no_permission()
            if not member.user == self.request.user:
                return self.handle_no_permission()
            return super().dispatch(request, *args, **kwargs)

        if server:
            person = Person.objects.get(user=self.request.user)
            try:
                ServerToMember.objects.get(member=person, server=server)
                return super().dispatch(request, *args, **kwargs)
            except (Person.DoesNotExist, ServerToMember.DoesNotExist):
                return self.handle_no_permission()


class DeviceEditForm(forms.ModelForm):
    """Default form for device edit. Initially only has device name only."""

    ALLOW_EDIT_FIELDS = ("name",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name not in self.ALLOW_EDIT_FIELDS:
                field.widget.attrs["readonly"] = True
                field.required = False

        self.helper = FormHelper(self)
        self.helper.add_input(Submit("submit", _("Save Details")))

    class Meta:
        model = vpnmodels.Device
        fields = ["name", "ip_address"]

    @property
    def allowed_cleaned_data(self):
        return {k: v for k, v in self.cleaned_data.items() if k in self.ALLOW_EDIT_FIELDS}

    def validate_unique(self):
        pass


class DeviceVPNListView(TemplateView):
    template_name = "selfservice/device_list.html"

    def get_context_data(self, **kwargs):
        servers = vpnmodels.VpnServer.get_servers_for_user(self.request.user)
        devices = vpnmodels.Device.get_devices_for_user(self.request.user)

        context = super().get_context_data(**kwargs)
        context.update(
            {
                "servers_and_devices": [
                    {
                        "server": server,
                        "devices": list(filter(lambda d: d.server_to_member.server_id == server.id, devices)),
                    }
                    for server in servers
                ]
            }
        )
        return context


class BaseVPNDeviceConfigView(PermissionRequiredMixin, OwnDeviceCheckMixin, View):
    permission_required = "hidl_vpn.resetconfig-vpndevice_selfservice"
    """Base class for the reveal config view. This view is invoked when user hits 'regenerate' or 'reveal' config on the
    device settings. It is post only since we do not store private keys, and as such they have to be re-generated every
    time user gets them. """

    def post(self, request, device):
        raise NotImplementedError


class DefaultVPNDeviceEditView(PermissionRequiredMixin, OwnDeviceCheckMixin, View):
    permission_required = "hidl_vpn.change_vpndevice_selfservice"
    _FORM_CLASS = DeviceEditForm
    _TEMPLATE_NAME = "selfservice/device_edit.html"

    def _get_form_class(self):
        return self._FORM_CLASS

    def post(self, request, device):
        form = self.create_form(request.POST)
        if form.is_valid():
            try:
                device.update_fields(**form.allowed_cleaned_data)
                messages.add_message(request, messages.INFO, _("Saved device successfully."))
                return self.get(request, device)
            except Exception as e:
                messages.add_message(request, messages.ERROR, _("Error saving device: %(error)s." % {"error": e}))
                return self.get(request, device)
        else:
            return render(
                request,
                self._TEMPLATE_NAME,
                {
                    "form": form,
                    "device": device,
                },
            )

    def create_form(self, *args, **kwargs):
        return self._get_form_class()(*args, **kwargs)

    def get(self, request, device):
        form = self.create_form(instance=device)
        return render(
            request,
            self._TEMPLATE_NAME,
            {
                "form": form,
                "device": device,
            },
        )


class DefaultVPNDeviceAddView(abc.ABC, PermissionRequiredMixin, OwnDeviceCheckMixin, View):
    permission_required = "hidl_vpn.create_vpndevice_selfservice"

    _FORM_CLASS = DeviceEditForm
    _TEMPLATE_NAME = "selfservice/device_edit.html"

    @classmethod
    def _get_form_class(cls):
        return cls._FORM_CLASS

    @abc.abstractmethod
    def create_device_instance(self, server_to_member, **kwargs) -> Device:
        """An internal method to create a new instance of the underlying device.
        kwargs would contain the form data to initialize the new object"""
        raise NotImplementedError

    def post(self, request, server):
        try:
            # Ensuring that we have access to this server (via server-to-member).
            person = coremodels.Person.objects.get(user_id=request.user.id)
            server_to_member = vpnmodels.ServerToMember.objects.select_related("member").get(
                member=person, server=server
            )

            form = self._get_form_class()(request.POST)
            if form.is_valid():
                device = self.create_device_instance(server_to_member, **form.cleaned_data)
                messages.add_message(request, messages.INFO, _("Created new device successfully."))
                return HttpResponseRedirect(reverse("selfservice:device_edit", args=[device.pk]))
            else:
                return render(
                    request,
                    self._TEMPLATE_NAME,
                    {"form": form},
                )

        except (coremodels.Person.DoesNotExist, vpnmodels.ServerToMember.DoesNotExist):
            messages.add_message(request, messages.ERROR, _("No access to given VPN Server."))
            return HttpResponseRedirect(request.path)

    def get(self, request, server):
        form = self._get_form_class()
        form.name = _("New device")

        return render(
            request,
            self._TEMPLATE_NAME,
            {"form": form},
        )


class VPNServiceViews(object):
    @cached_property
    def vpn_details_view(self) -> BaseVPNDeviceConfigView:
        raise NotImplementedError

    @cached_property
    def vpn_device_edit_view(self) -> DefaultVPNDeviceEditView:
        return DefaultVPNDeviceEditView.as_view()

    @cached_property
    def vpn_device_add_view(self) -> DefaultVPNDeviceEditView:
        return DefaultVPNDeviceAddView.as_view()
