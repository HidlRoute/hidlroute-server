from autoslug import AutoSlugField
from django.db import models


class Nameable(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length=1024, null=False, blank=False)
    slug = AutoSlugField(populate_from='name', max_length=20, editable=True, null=False, blank=False, db_index=True,
                         unique=True)


class WithComment(models.Model):
    class Meta:
        abstract = True

    comment = models.TextField(null=False, blank=True)
