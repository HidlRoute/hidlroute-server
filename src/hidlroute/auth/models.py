from typing import Optional, Iterable

from django.contrib.auth.models import AbstractUser as DjangoUser
from django.contrib.auth.models import Group as DjangoGroup
from django.utils.translation import gettext_lazy as _
from django.db import models, transaction

from hidlroute.core.models import Person, Group


class User(DjangoUser):
    class Meta:
        db_table = 'auth_user'

    profile_picture = models.URLField(null=True, blank=True)

    @transaction.atomic
    def save(self, *args, **kwargs) -> None:
        is_insert = self.pk is None
        super().save(*args, **kwargs)
        if is_insert:
            Person.objects.create(user=self, group_id=Group.DEFAULT_GROUP_ID)


class Role(DjangoGroup):
    """Instead of trying to get new user under existing `Aunthentication and Authorization`
    banner, create a proxy group model under our Accounts app label.
    Refer to: https://github.com/tmm/django-username-email/blob/master/cuser/admin.py
    """

    class Meta:
        verbose_name = _('role')
        verbose_name_plural = _('roles')
        app_label = 'hidl_auth'
        db_table = 'hidl_auth_role'
        proxy = True
