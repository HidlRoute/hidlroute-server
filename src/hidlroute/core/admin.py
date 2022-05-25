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

from typing import Any, Optional, Type, List, Union, Sequence, Callable

from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from django import forms
from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.db.models import QuerySet, TextField
from django.db.models.fields.related import RelatedField
from django.forms import widgets, BaseModelFormSet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import path, reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django_reverse_admin import ReverseModelAdmin
from polymorphic.admin import PolymorphicChildModelAdmin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from hidlroute.core import models
from hidlroute.core.admin_commons import (
    HidlBaseModelAdmin,
    GroupSelectAdminMixin,
    HidlePolymorphicParentAdmin,
    HidlePolymorphicChildAdmin,
    ManagedRelActionsMixin,
)
from hidlroute.core.factory import default_service_factory
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
from hidlroute.core.service.base import ServerState, HidlNetworkingException


# from django.utils.translation import gettext_lazy as _


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


class ServerToMemberAdmin(ManagedRelActionsMixin, admin.TabularInline):
    model = models.ServerToMember
    extra = 0
    verbose_name = _("Member")
    verbose_name_plural = _("Members")


class ServerToGroupAdmin(GroupSelectAdminMixin, ManagedRelActionsMixin, admin.TabularInline):
    model = models.ServerToGroup
    extra = 0
    verbose_name = _("Group")
    verbose_name_plural = _("Groups")


class ServerRelatedAdminMixin:
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
        qs = self.model.load_related_to_server(self.parent_obj)
        return qs


class ClientRoutingRuleAdmin(GroupSelectAdminMixin, ServerRelatedAdminMixin, admin.TabularInline):
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


class ServerRoutingRulesInlineAdmin(GroupSelectAdminMixin, ServerRelatedAdminMixin, admin.StackedInline):
    model = models.ServerRoutingRule
    fields = ("network", "gateway", "interface", ("server_group", "server_member"), "comment")
    extra = 0


class RelatedFirewallRulesReadonlyInline(SortableInlineAdminMixin, admin.TabularInline):
    ordering = ["order"]
    model = models.VpnFirewallRule
    fields = [
        "order",
        "description",
    ]
    readonly_fields = [
        "description",
    ]
    extra = 0
    template = "admin/hidl_core/server/firewall_inline.html"
    verbose_name = _("Firewall Rule")
    verbose_name_plural = _("Firewall Rules")

    def has_add_permission(self, request: HttpRequest, obj=None) -> bool:
        return False


class BaseServerAdminImpl(ManagedRelActionsMixin, SortableAdminMixin, PolymorphicChildModelAdmin):
    ICON = "images/server/no-icon.png"
    ordering = ["id"]
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
    inlines = [
        ServerToGroupAdmin,
        ServerToMemberAdmin,
        RelatedFirewallRulesReadonlyInline,
        ServerRoutingRulesInlineAdmin,
        ClientRoutingRuleAdmin,
    ]
    create_inlines = [ServerToGroupAdmin]

    def get_inlines(self, request: HttpRequest, obj: Optional[models.Server] = None) -> List[Type[InlineModelAdmin]]:
        is_create = obj is None
        if is_create and self.create_inlines is not None:
            return self.create_inlines
        else:
            return self.inlines

    def get_urls(self):
        custom_urls = [
            path(
                "startserver/<int:server_id>",
                self.admin_site.admin_view(self.action_start_server),
                name="startserver_url",
            ),
            path(
                "stopserver/<int:server_id>", self.admin_site.admin_view(self.action_stop_server), name="stopserver_url"
            ),
            path(
                "restartserver/<int:server_id>",
                self.admin_site.admin_view(self.action_restart_server),
                name="restartserver_url",
            ),
        ]
        return custom_urls + super().get_urls()

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
        if "_start_server" in request.POST:
            return self.action_start_server(request, obj.pk)
        elif "_stop_server" in request.POST:
            return self.action_stop_server(request, obj.pk)
        elif "_restart_server" in request.POST:
            return self.action_restart_server(request, obj.pk)
        return super().response_change(request, obj)

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

    def __get_server_state_change_redirect_url(self, request: HttpRequest) -> str:
        return reverse("admin:hidl_core_server_changelist") + "?server-started=1"

    def action_start_server(self, request: HttpRequest, server_id: int) -> HttpResponse:
        try:
            obj = models.Server.objects.get(pk=server_id)
            obj.start()
            self.message_user(request, _("Server {} is starting".format(obj)))
        except HidlNetworkingException as e:
            messages.error(request, _("Error starting server. Details: {}".format(e)))

        return HttpResponseRedirect(self.__get_server_state_change_redirect_url(request))

    def action_stop_server(self, request: HttpRequest, server_id: int) -> HttpResponse:
        try:
            obj = models.Server.objects.get(pk=server_id)
            obj.stop()
            self.message_user(request, _("Server {} is shutting down".format(obj)))
        except HidlNetworkingException as e:
            messages.error(request, _("Error stopping server. Details: {}".format(e)))

        return HttpResponseRedirect(self.__get_server_state_change_redirect_url(request))

    def action_restart_server(self, request: HttpRequest, server_id: int) -> HttpResponse:
        obj = models.Server.objects.get(pk=server_id)
        self.message_user(request, _("Server {} is re-starting".format(obj)))
        obj.restart()
        return HttpResponseRedirect(self.__get_server_state_change_redirect_url(request))

    def get_changelist_instance(self, request):
        instance = super().get_changelist_instance(request)
        self.enable_sorting = False
        return instance

    def get_list_display(self, request):
        return super(PolymorphicChildModelAdmin, self).get_list_display(request)


@admin.register(models.Server)
class ServerAdmin(HidlBaseModelAdmin, HidlePolymorphicParentAdmin):
    Impl = BaseServerAdminImpl
    base_model = models.Server
    child_models = []
    add_type_form = ServerTypeSelectForm
    ordering = ["id"]
    list_display = ["__str__", "subnet", "ip_address", "vpn_status", "control_button"]
    readonly_fields = ["vpn_status"]
    polymorphic_list = True
    control_buttons_template = loader.get_template("admin/hidl_core/server/server_control_buttons.html")

    def vpn_status(self, obj: models.Server):
        state = obj.status.state
        css_class = "badge-secondary"
        if state.is_transitioning:
            css_class = "badge-primary"
        elif state == ServerState.FAILED:
            css_class = "badge-danger"
        elif state.is_running:
            css_class = "badge-success"
        result = f'<span class="server-state badge {css_class}">{state.label}</span>'
        if obj.has_pending_changes:
            result += f'&nbsp;<span class="server-state badge badge-warning">{_("Changes Pending")}</span>'
        return mark_safe(result)

    def control_button(self, obj: models.Server):
        return self.control_buttons_template.render(context={"server": obj, "ServerState": ServerState})

    control_button.short_description = _("Actions")

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


@admin.register(models.FirewallService)
class FirewallServiceAdmin(HidlBaseModelAdmin):
    list_display = ["name", "slug", "comment"]
    inlines = [PortRangeAdmin]
    fieldsets = [
        (None, {"fields": ("name",)}),
    ]


class ServerFirewallRuleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        supported_actions = [(x, x) for x in default_service_factory.firewall_service.get_supported_actions()]
        self.fields["action"].widget = forms.widgets.Select(choices=supported_actions)
        self.fields["server"].widget = forms.widgets.HiddenInput()


class NetworkFilterInline(ManagedRelActionsMixin, admin.TabularInline):
    model = models.VpnNetworkFilter
    template = "admin/hidl_core/network_filter/tabular_inline.html"
    extra = 0
    fields = ["server_group", "server_member", "custom", "subnet"]
    select_related = ["server_group__group"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.parent_instance: Optional[models.VpnFirewallRule] = None
        self.template = self.__class__.template
        self.can_delete = False

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

    def get_field_queryset(
        self, db: None, db_field: RelatedField, request: Optional[HttpRequest]
    ) -> Optional[QuerySet]:
        qs = super().get_field_queryset(db, db_field, request)
        if qs is None:
            qs = db_field.remote_field.model._default_manager.using(db)
        if self.parent_instance and db_field.related_model in (models.ServerToMember, models.ServerToGroup):
            qs.filter(server=self.parent_instance.server)
        return qs


@admin.register(models.VpnFirewallRule)
class ServerFirewallRuleAdmin(SortableAdminMixin, HidlBaseModelAdmin, ReverseModelAdmin):
    ordering = ["order"]
    list_display = ["order", "__str__"]
    form = ServerFirewallRuleForm
    inline_reverse = [
        {"admin_class": NetworkFilterInline, "field_name": "network_from", "kwargs": {}},
        {"admin_class": NetworkFilterInline, "field_name": "network_to", "kwargs": {}},
    ]
    inline_type = "tabular"
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "server",
                    ("action", "service"),
                )
            },
        ),
        HidlBaseModelAdmin.with_comment_fieldset,
    )
    jazzmin_section_order = (None, _("From"), _("To"), HidlBaseModelAdmin.with_comment_fieldset[0])

    def get_inline_instances(self, request, obj=None):
        instances = super().get_inline_instances(request, obj)
        for x in instances:
            if isinstance(x, NetworkFilterInline):
                x.parent_instance = obj
        return instances

    def response_add(
        self, request: HttpRequest, obj: models.VpnFirewallRule, post_url_continue: Optional[str] = None
    ) -> HttpResponse:
        original_response = super().response_add(request, obj, post_url_continue)
        if "_continue" not in request.POST:
            return HttpResponseRedirect(obj.server.get_admin_url() + "#firewall-rules-tab")
        return original_response

    def response_change(self, request: HttpRequest, obj: models.VpnFirewallRule) -> HttpResponse:
        original_response = super().response_change(request, obj)
        if "_continue" not in request.POST:
            return HttpResponseRedirect(obj.server.get_admin_url() + "#firewall-rules-tab")
        return original_response


@admin.register(models.ServerRoutingRule)
class ServerRoutingRuleAdmin(HidlBaseModelAdmin):
    fieldsets = (
        (None, {"fields": ["network", "gateway", "interface"]}),
        HidlBaseModelAdmin.attachable_fieldset,
        HidlBaseModelAdmin.with_comment_fieldset,
    )
    list_select_related = ["network"]


@admin.register(models.Subnet)
class SubnetAdmin(HidlBaseModelAdmin):
    fieldsets = (
        (None, {"fields": HidlBaseModelAdmin.nameable_fields + ["cidr"]}),
        HidlBaseModelAdmin.with_comment_fieldset,
    )
