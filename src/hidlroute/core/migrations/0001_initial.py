# Generated by Django 4.0.4 on 2022-05-17 10:01

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

import autoslug.fields
import cidrfield.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import hidlroute.core.models
from django.utils.translation import gettext_lazy as _


def insert_default_group(apps, schema_editor):
    from hidlroute.core.models import Group

    Group.add_root(slug=Group.DEFAULT_GROUP_SLUG, name=_("DEFAULT"))


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="ClientConfig",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("DNS", models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name="Group",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=1024)),
                (
                    "slug",
                    autoslug.fields.AutoSlugField(
                        blank=True, editable=True, max_length=20, populate_from="name", unique=True
                    ),
                ),
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
            name="Server",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=1024)),
                (
                    "slug",
                    autoslug.fields.AutoSlugField(
                        blank=True, editable=True, max_length=20, populate_from="name", unique=True
                    ),
                ),
                ("comment", models.TextField(blank=True)),
                ("interface_name", models.CharField(max_length=16)),
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
            name="ServerRule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("comment", models.TextField(blank=True)),
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
        ),
        migrations.CreateModel(
            name="ServerToGroup",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("group", models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to="hidl_core.group")),
                ("server", models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to="hidl_core.server")),
            ],
            options={
                "verbose_name": "Group",
                "verbose_name_plural": "Groups",
                "unique_together": {("server", "group")},
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
                ("host_name", models.SlugField(max_length=100)),
            ],
            options={
                "abstract": False,
            },
            bases=("hidl_core.member",),
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
            ],
            options={
                "abstract": False,
            },
            bases=("hidl_core.member",),
        ),
        migrations.CreateModel(
            name="ServerFirewallRule",
            fields=[
                (
                    "serverrule_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="hidl_core.serverrule",
                    ),
                ),
                ("order", models.PositiveIntegerField(default=0)),
                ("action", models.CharField(max_length=16)),
            ],
            options={
                "abstract": False,
            },
            bases=("hidl_core.serverrule", models.Model),
        ),
        migrations.CreateModel(
            name="ServerRoutingRule",
            fields=[
                (
                    "serverrule_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="hidl_core.serverrule",
                    ),
                ),
                ("network", cidrfield.models.IPNetworkField()),
                ("gateway", cidrfield.models.IPNetworkField()),
                ("interface", models.CharField(max_length=16)),
            ],
            options={
                "abstract": False,
            },
            bases=("hidl_core.serverrule",),
        ),
        migrations.CreateModel(
            name="Subnet",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=1024)),
                (
                    "slug",
                    autoslug.fields.AutoSlugField(
                        blank=True, editable=True, max_length=20, populate_from="name", unique=True
                    ),
                ),
                ("comment", models.TextField(blank=True)),
                ("cidr", cidrfield.models.IPNetworkField()),
                (
                    "server_group",
                    models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to="hidl_core.servertogroup"),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ServerToMember",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("member", models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to="hidl_core.member")),
                ("server", models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to="hidl_core.server")),
            ],
            options={
                "verbose_name": "Member",
                "verbose_name_plural": "Members",
                "unique_together": {("server", "member")},
            },
        ),
        migrations.AddField(
            model_name="serverrule",
            name="server_group",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to="hidl_core.servertogroup"
            ),
        ),
        migrations.AddField(
            model_name="serverrule",
            name="server_member",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to="hidl_core.servertomember"
            ),
        ),
        migrations.AddField(
            model_name="member",
            name="servers",
            field=models.ManyToManyField(through="hidl_core.ServerToMember", to="hidl_core.server"),
        ),
        migrations.AddField(
            model_name="group",
            name="servers",
            field=models.ManyToManyField(through="hidl_core.ServerToGroup", to="hidl_core.server"),
        ),
        migrations.CreateModel(
            name="Device",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("comment", models.TextField(blank=True)),
                ("address", cidrfield.models.IPNetworkField(validators=[hidlroute.core.models.should_be_single_IP])),
                (
                    "server_member",
                    models.ForeignKey(
                        null=True, on_delete=django.db.models.deletion.RESTRICT, to="hidl_core.servertomember"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddConstraint(
            model_name="serverrule",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(("server_group__isnull", True), ("server_member__isnull", False)),
                    models.Q(("server_group__isnull", False), ("server_member__isnull", True)),
                    _connector="OR",
                ),
                name="check_serverrule_for_member_xor_group",
            ),
        ),
        migrations.AddField(
            model_name="person",
            name="user",
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.RunPython(insert_default_group),
    ]
