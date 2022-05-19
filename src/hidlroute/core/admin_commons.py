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

from django.contrib.admin.options import BaseModelAdmin
from django.utils.translation import gettext_lazy as _
from django.db.models import ForeignKey
from django.forms import ModelChoiceField
from django.http import HttpRequest
from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin

from hidlroute.core import models as core_models


class GroupSelectAdminMixin(BaseModelAdmin):
    def formfield_for_foreignkey(
        self, db_field: ForeignKey, request: Optional[HttpRequest], **kwargs: Any
    ) -> Optional[ModelChoiceField]:
        form_field: ModelChoiceField = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.related_model == core_models.Group:
            form_field.queryset = core_models.Group.get_tree()
            form_field.label_from_instance = lambda obj: " / ".join([x.name for x in obj.get_ancestors()] + [obj.name])
        return form_field


class HidlBaseModelAdmin(GroupSelectAdminMixin, admin.ModelAdmin):
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
    def register_implementation(cls, *args):
        def _wrap(impl_admin_cls):
            if impl_admin_cls.base_model not in cls.child_models:
                cls.child_models.append(impl_admin_cls.base_model)
            if not admin.site.is_registered(impl_admin_cls.base_model):
                admin.site.register(impl_admin_cls.base_model, impl_admin_cls)
            return impl_admin_cls

        return _wrap


class HidlePolymorphicChildAdmin(PolymorphicChildModelAdmin):
    show_in_index = False
