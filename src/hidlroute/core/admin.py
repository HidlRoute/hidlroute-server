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

from typing import Any, Optional, Union, Sequence, Callable

from django import forms
from django.contrib import admin
from django.http import HttpRequest
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

import hidlroute.core.models
from hidlroute.core import models
from hidlroute.core.admin_commons import (
    HidlBaseModelAdmin,
)
from hidlroute.core.factory import default_service_factory


@admin.register(models.Host)
class HostAdmin(HidlBaseModelAdmin):
    base_model = models.Host
    show_in_index = True


@admin.register(models.Group)
class GroupAdmin(TreeAdmin):
    form = movenodeform_factory(models.Group)


class PortRanceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class PortRangeAdmin(admin.TabularInline):
    model = models.FirewallPortRange
    form = PortRanceForm
    extra = 0

    def get_fields(self, request: HttpRequest, obj: Optional[Any] = None) -> Sequence[Union[Callable, str]]:
        fields = super().get_fields(request, obj)

        return fields

    def formfield_for_dbfield(self, db_field, request: Optional[HttpRequest], **kwargs: Any) -> Optional[forms.Field]:
        field = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == "protocol":
            supported_protocols = [(x, x) for x in default_service_factory.firewall_service.get_supported_protocols()]
            field.widget = forms.widgets.Select(choices=supported_protocols)
        return field


@admin.register(hidlroute.core.models.FirewallService)
class FirewallServiceAdmin(HidlBaseModelAdmin):
    list_display = ["name", "slug", "comment"]
    inlines = [PortRangeAdmin]
    fieldsets = [
        (None, {"fields": ("name",)}),
    ]


@admin.register(models.Subnet)
class SubnetAdmin(HidlBaseModelAdmin):
    fieldsets = (
        (None, {"fields": HidlBaseModelAdmin.nameable_fields + ["cidr"]}),
        HidlBaseModelAdmin.with_comment_fieldset,
    )
