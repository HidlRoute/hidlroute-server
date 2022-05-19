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

from typing import Any, Optional, Type, List

from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet, TextField
from django.forms import widgets, BaseModelFormSet
from django.http import HttpRequest, HttpResponse
from polymorphic.admin import PolymorphicChildModelAdmin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

# from django.utils.translation import gettext_lazy as _

from hidlroute.core import models
from hidlroute.core.admin_commons import (
    HidlBaseModelAdmin,
    GroupSelectAdminMixin,
    HidlePolymorphicParentAdmin,
    HidlePolymorphicChildAdmin,
)
from hidlroute.core.forms import ServerTypeSelectForm


# @admin.register(models.Member)
# class MemberAdmin(GroupSelectAdminMixin, PolymorphicParentModelAdmin):
#     base_model = models.Member
#     child_models = (
#         models.Person,
#         models.Host,
#     )
#     list_filter = (PolymorphicChildModelFilter,)
#
#     def get_child_type_choices(self, request, action):
#         return [(k, v.capitalize()) for k, v, in super().get_child_type_choices(request, action)]
#
#
# @admin.register(models.Person)
# class PersonAdmin(GroupSelectAdminMixin, PolymorphicChildModelAdmin):
#     base_model = models.Person
#     show_in_index = False


@admin.register(models.Host)
class HostAdmin(HidlBaseModelAdmin):
    base_model = models.Host
    show_in_index = True


class BaseChildDeviceAdmin(HidlePolymorphicChildAdmin):
    pass


@admin.register(models.Device)
class DeviceAdmin(HidlBaseModelAdmin, HidlePolymorphicParentAdmin):
    Impl = BaseChildDeviceAdmin
    base_model = models.Device
    child_models = []


class ServerToMemberAdmin(admin.TabularInline):
    model = models.ServerToMember
    extra = 0


class ServerToGroupAdmin(GroupSelectAdminMixin, admin.TabularInline):
    model = models.ServerToGroup
    extra = 0


class ClientRoutingRuleAdmin(admin.TabularInline):
    model = models.ClientRoutingRule
    extra = 0
    fields = (
        "network",
        "server_group",
        "server_member",
        "comment",
    )
    formfield_overrides = {
        TextField: {"widget": widgets.TextInput},
    }

    def __init__(self, parent_model, admin_site) -> None:
        super().__init__(parent_model, admin_site)
        self.parent_obj: Optional[models.Server] = None

    def get_formset(self, request, obj=None, **kwargs):
        if self.parent_obj is None and obj:
            self.parent_obj = obj

        original_formset = super().get_formset(request, obj, **kwargs)

        def modified_constructor(
            _self,
            data=None,
            files=None,
            instance=None,
            save_as_new=False,
            prefix=None,
            queryset=None,
            **kwargs,
        ):
            if instance is None:
                _self.instance = _self.fk.remote_field.model()
            else:
                _self.instance = instance
            _self.save_as_new = save_as_new
            if queryset is None:
                queryset = _self.model._default_manager
            BaseModelFormSet.__init__(_self, data, files, prefix=prefix, queryset=queryset, **kwargs)

            # Add the generated field to form._meta.fields if it's defined to make
            # sure validation isn't skipped on that field.
            if _self.form._meta.fields and _self.fk.name not in _self.form._meta.fields:
                if isinstance(_self.form._meta.fields, tuple):
                    _self.form._meta.fields = list(_self.form._meta.fields)
                _self.form._meta.fields.append(_self.fk.name)

        # We replaced original constructor to avoid limiting fieldset by server_id
        original_formset.__init__ = modified_constructor
        return original_formset

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        qs = models.ClientRoutingRule.load_related_to_server(self.parent_obj)
        return qs


class BaseServerAdminImpl(PolymorphicChildModelAdmin):
    ICON = "images/server/no-icon.png"
    fieldsets = [
        (
            None,
            {
                "fields": HidlBaseModelAdmin.nameable_fields
                + [
                    "interface_name",
                    ("subnet", "ip_address"),
                    "comment",
                ]
            },
        ),
    ]
    inlines = [ServerToGroupAdmin, ServerToMemberAdmin, ClientRoutingRuleAdmin]
    create_inlines = [ServerToGroupAdmin]

    def get_inlines(self, request: HttpRequest, obj: Optional[models.Server] = None) -> List[Type[InlineModelAdmin]]:
        is_create = obj is None
        if is_create and self.create_inlines is not None:
            return self.create_inlines
        else:
            return self.inlines

    @classmethod
    def get_icon(cls) -> str:
        return cls.ICON

    def response_add(self, request: HttpRequest, obj: models.Server, post_url_continue=None) -> HttpResponse:
        # We should allow further modification of the user just added i.e. the
        # 'Save' button should behave like the 'Save and continue editing'
        # button except of:
        # * The user has pressed the 'Save and add another' button
        if "_addanother" not in request.POST:
            request.POST = request.POST.copy()  # noqa
            request.POST["_continue"] = 1  # noqa
        return super().response_add(request, obj, post_url_continue)

    def response_change(self, request: HttpRequest, obj: models.Server) -> HttpResponse:
        # Stay on the edit page unless Add Another button is pressed
        if "_addanother" not in request.POST:
            request.POST = request.POST.copy()  # noqa
            request.POST["_continue"] = 1  # noqa
        return super().response_add(request, obj)

    def save_formset(self, request: Any, form: Any, formset: Any, change: Any) -> None:
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            if isinstance(instance, models.ServerRelated):
                if instance.server_group is not None or instance.server_member is not None:
                    instance.server = None
            instance.save()
        formset.save_m2m()


@admin.register(models.Server)
class ServerAdmin(HidlBaseModelAdmin, HidlePolymorphicParentAdmin):
    Impl = BaseServerAdminImpl
    base_model = models.Server
    child_models = []
    add_type_form = ServerTypeSelectForm

    def get_child_type_choices(self, request, action):
        """
        Return a list of polymorphic types for which the user has the permission to perform the given action.
        """
        self._lazy_setup()
        choices = []
        content_types = ContentType.objects.get_for_models(*self.get_child_models(), for_concrete_models=False)

        for model, ct in content_types.items():
            perm_function_name = f"has_{action}_permission"
            model_admin = self._get_real_admin_by_model(model)
            perm_function = getattr(model_admin, perm_function_name)
            if not perm_function(request):
                continue
            choices.append((ct.id, dict(name=model._meta.verbose_name, image=model_admin.get_icon())))
        return choices


@admin.register(models.Group)
class GroupAdmin(TreeAdmin):
    form = movenodeform_factory(models.Group)


@admin.register(models.ServerFirewallRule)
class ServerFirewallRuleAdmin(SortableAdminMixin, HidlBaseModelAdmin):
    ordering = ["order"]
    list_display = ["order", "__str__"]
    fieldsets = (
        (None, {"fields": ("action",)}),
        HidlBaseModelAdmin.attachable_fieldset,
        HidlBaseModelAdmin.with_comment_fieldset,
    )


@admin.register(models.ServerRoutingRule)
class ServerRoutingRuleAdmin(HidlBaseModelAdmin):
    fieldsets = (
        (None, {"fields": ["network", "gateway", "interface"]}),
        HidlBaseModelAdmin.attachable_fieldset,
        HidlBaseModelAdmin.with_comment_fieldset,
    )


@admin.register(models.Subnet)
class SubnetAdmin(HidlBaseModelAdmin):
    fieldsets = (
        (None, {"fields": HidlBaseModelAdmin.nameable_fields + ["cidr"]}),
        HidlBaseModelAdmin.with_comment_fieldset,
    )
