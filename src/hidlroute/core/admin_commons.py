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

from typing import Optional, Any

import netfields
from django import forms
from django.contrib.admin.options import BaseModelAdmin
from django.contrib.admin.widgets import AdminTextInputWidget
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.http import HttpRequest
from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin

from hidlroute.core import models as core_models


class GroupSelectAdminMixin(BaseModelAdmin):
    def formfield_for_dbfield(
        self, db_field: models.Field, request: Optional[HttpRequest], **kwargs: Any
    ) -> Optional[forms.Field]:
        form_field = super().formfield_for_dbfield(db_field, request, **kwargs)
        if form_field.__class__ == forms.ModelChoiceField and db_field.related_model == core_models.Group:
            form_field.queryset = core_models.Group.get_tree()
            form_field.label_from_instance = lambda obj: obj.get_full_name()
        return form_field


class ManagedRelActionsMixin(BaseModelAdmin):
    def formfield_for_dbfield(
        self, db_field: models.Field, request: Optional[HttpRequest], **kwargs: Any
    ) -> Optional[forms.Field]:
        form_field = super().formfield_for_dbfield(db_field, request, **kwargs)
        if form_field.__class__ == forms.ModelChoiceField:
            form_field.widget.can_delete_related = False
            # form_field.widget.can_change_related = False
        return form_field


class HidlFormsMixin:
    pass
    formfield_overrides = {
        netfields.InetAddressField: dict(widget=AdminTextInputWidget),
        netfields.CidrAddressField: dict(widget=AdminTextInputWidget),
    }


class HidlBaseModelAdmin(ManagedRelActionsMixin, GroupSelectAdminMixin, HidlFormsMixin, admin.ModelAdmin):
    with_comment_fieldset = (_("Notes"), {"fields": ("comment",)})
    nameable_fields = [
        ("name", "slug"),
    ]
    attachable_fieldset = (
        _("Attachment"),
        {
            "fields": ["server", "server_group", "server_member"],
            "description": _("Pick one of the entities to attach the rules."),
        },
    )


class HidlePolymorphicParentAdmin(PolymorphicParentModelAdmin):
    @classmethod
    def register_implementation(cls, model):
        def _wrap(impl_admin_cls):
            if model not in cls.child_models:
                cls.child_models.append(model)
            if not admin.site.is_registered(model):
                admin.site.register(model, impl_admin_cls)
            return impl_admin_cls

        return _wrap


class HidlePolymorphicChildAdmin(PolymorphicChildModelAdmin):
    show_in_index = False
