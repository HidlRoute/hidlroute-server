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

from django.db.models import ForeignKey
from django.forms import ModelChoiceField
from django.http import HttpRequest
from django.contrib import admin

from hidlroute.core import models as core_models


class GroupSelectAdminMixin(object):
    def formfield_for_foreignkey(
            self, db_field: ForeignKey, request: Optional[HttpRequest], **kwargs: Any
    ) -> Optional[ModelChoiceField]:
        form_field: ModelChoiceField = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.related_model == core_models.Group:
            form_field.queryset = core_models.Group.get_tree()
            form_field.label_from_instance = lambda obj: " / ".join([x.name for x in obj.get_ancestors()] + [obj.name])
        return form_field


class HidlBaseModelAdmin(GroupSelectAdminMixin, admin.ModelAdmin):
    pass
