# Generated by Django 4.0.4 on 2022-05-27 16:57

import autoslug.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import netfields.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="FirewallService",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "slug",
                    autoslug.fields.AutoSlugField(
                        blank=True, editable=True, max_length=150, populate_from="name", unique=True
                    ),
                ),
                ("name", models.CharField(max_length=1024)),
                ("comment", models.TextField(blank=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Group",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "slug",
                    autoslug.fields.AutoSlugField(
                        blank=True, editable=True, max_length=150, populate_from="name", unique=True
                    ),
                ),
                ("name", models.CharField(max_length=1024)),
                ("comment", models.TextField(blank=True)),
                ("path", models.CharField(max_length=255, unique=True)),
                ("depth", models.PositiveIntegerField()),
                ("numchild", models.PositiveIntegerField(default=0)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Member",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("comment", models.TextField(blank=True)),
                ("group", models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to="hidl_core.group")),
                (
                    "polymorphic_ctype",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="polymorphic_%(app_label)s.%(class)s_set+",
                        to="contenttypes.contenttype",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Subnet",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "slug",
                    autoslug.fields.AutoSlugField(
                        blank=True, editable=True, max_length=150, populate_from="name", unique=True
                    ),
                ),
                ("name", models.CharField(max_length=1024)),
                ("comment", models.TextField(blank=True)),
                ("cidr", netfields.fields.CidrAddressField(max_length=43)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Host",
            fields=[
                (
                    "member_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="hidl_core.member",
                    ),
                ),
                ("host_name", models.SlugField(max_length=100, unique=True)),
            ],
            options={
                "abstract": False,
            },
            bases=("hidl_core.member",),
        ),
        migrations.CreateModel(
            name="FirewallPortRange",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("protocol", models.CharField(blank=True, max_length=20, null=True)),
                ("start", models.PositiveIntegerField()),
                ("end", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "service",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="hidl_core.firewallservice"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Person",
            fields=[
                (
                    "member_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="hidl_core.member",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("hidl_core.member",),
        ),
    ]
