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

from autoslug import AutoSlugField
from django.db import models


class Identifiable(models.Model):
    class Meta:
        abstract = True

    slug = AutoSlugField(
        populate_from="name", max_length=150, editable=True, null=False, blank=True, db_index=True, unique=True
    )


class Nameable(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length=1024, null=False, blank=False)

    def __str__(self) -> str:
        return self.name


class NameableIdentifiable(Nameable, Identifiable):
    class Meta:
        abstract = True


class WithComment(models.Model):
    class Meta:
        abstract = True

    comment = models.TextField(null=False, blank=True)


class WithReprCache(models.Model):
    class Meta:
        abstract = True

    repr_cache = models.CharField(max_length=200, null=True, blank=True)

    @property
    def repr(self):
        if self.repr_cache:
            return self.repr_cache
        else:
            return self._get_repr()

    def _get_repr(self):
        raise NotImplementedError

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None) -> None:
        self.repr_cache = self._get_repr()
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self) -> str:
        if self.repr_cache:
            return self.repr_cache
        return super().__str__()


class Sortable(models.Model):
    class Meta:
        abstract = True

    order = models.PositiveIntegerField(default=0, null=False, blank=False)
