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


class Nameable(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length=1024, null=False, blank=False)
    slug = AutoSlugField(
        populate_from="name", max_length=20, editable=True, null=False, blank=True, db_index=True, unique=True
    )


class WithComment(models.Model):
    class Meta:
        abstract = True

    comment = models.TextField(null=False, blank=True)


class Sortable(models.Model):
    class Meta:
        abstract = True

    order = models.PositiveIntegerField(default=0, null=False, blank=False)
