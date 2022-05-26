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

from django.contrib.auth.models import AbstractUser as DjangoUser
from django.contrib.auth.models import Group as DjangoGroup
from django.utils.translation import gettext_lazy as _
from django.db import models, transaction

from hidlroute.core.base_models import WithComment
from hidlroute.core.models import Person, Group


class User(WithComment, DjangoUser):
    class Meta:
        db_table = "auth_user"
        permissions = [
            ("can_manage_defender", "Can manage defender"),
        ]

    profile_picture = models.URLField(null=True, blank=True)
    external_id = models.CharField(
        max_length=512,
        null=True,
        blank=True,
        help_text=_("Identifier in the external system. " "Might be useful for synchronization purposes"),
    )

    @transaction.atomic
    def save(self, *args, **kwargs) -> None:
        is_insert = self.pk is None
        super().save(*args, **kwargs)
        if is_insert:
            Person.objects.create(user=self, group=Group.get_default_group())


class Role(DjangoGroup):
    """Instead of trying to get new user under existing `Aunthentication and Authorization`
    banner, create a proxy group model under our Accounts app label.
    Refer to: https://github.com/tmm/django-username-email/blob/master/cuser/admin.py
    """

    class Meta:
        verbose_name = _("role")
        verbose_name_plural = _("roles")
        app_label = "hidl_auth"
        db_table = "hidl_auth_role"
        proxy = True
