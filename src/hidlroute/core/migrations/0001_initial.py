# Generated by Django 4.0.4 on 2022-05-14 13:01

import cidrfield.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import hidlroute.core.models


def insert_default_group(apps, schema_editor):
    from hidlroute.core.models import Group
    # Group = apps.get_model('hidl_core', 'Group')
    Group.add_root(name="DEFAULT", pk=Group.DEFAULT_GROUP_ID)


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ClientConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('DNS', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=255, unique=True)),
                ('depth', models.PositiveIntegerField()),
                ('numchild', models.PositiveIntegerField(default=0)),
                ('name', models.CharField(max_length=1024)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='hidl_core.group')),
                ('polymorphic_ctype',
                 models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE,
                                   related_name='polymorphic_%(app_label)s.%(class)s_set+',
                                   to='contenttypes.contenttype')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
        ),
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interface_name', models.CharField(max_length=16)),
                ('name', models.CharField(max_length=1024)),
            ],
        ),
        migrations.CreateModel(
            name='ServerGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='hidl_core.group')),
                ('server', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='hidl_core.server')),
            ],
        ),
        migrations.CreateModel(
            name='ServerRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('polymorphic_ctype',
                 models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE,
                                   related_name='polymorphic_%(app_label)s.%(class)s_set+',
                                   to='contenttypes.contenttype')),
                ('server_group',
                 models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='hidl_core.servergroup')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
        ),
        migrations.CreateModel(
            name='Host',
            fields=[
                ('member_ptr',
                 models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True,
                                      primary_key=True, serialize=False, to='hidl_core.member')),
                ('host_name', models.CharField(max_length=1024)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('hidl_core.member',),
        ),
        migrations.CreateModel(
            name='ServerFirewallRule',
            fields=[
                ('serverrule_ptr',
                 models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True,
                                      primary_key=True, serialize=False, to='hidl_core.serverrule')),
                ('action', models.CharField(max_length=16)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('hidl_core.serverrule',),
        ),
        migrations.CreateModel(
            name='ServerRoutingRule',
            fields=[
                ('serverrule_ptr',
                 models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True,
                                      primary_key=True, serialize=False, to='hidl_core.serverrule')),
                ('network', cidrfield.models.IPNetworkField()),
                ('gateway', cidrfield.models.IPNetworkField()),
                ('interface', models.CharField(max_length=16)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('hidl_core.serverrule',),
        ),
        migrations.CreateModel(
            name='Subnet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024)),
                ('cidr', cidrfield.models.IPNetworkField()),
                ('server_group',
                 models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='hidl_core.servergroup')),
            ],
        ),
        migrations.CreateModel(
            name='ServerToMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='hidl_core.member')),
                ('server', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='hidl_core.server')),
            ],
        ),
        migrations.AddField(
            model_name='serverrule',
            name='server_member',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='hidl_core.servertomember'),
        ),
        migrations.AddField(
            model_name='member',
            name='servers',
            field=models.ManyToManyField(through='hidl_core.ServerToMember', to='hidl_core.server'),
        ),
        migrations.AddField(
            model_name='group',
            name='servers',
            field=models.ManyToManyField(through='hidl_core.ServerGroup', to='hidl_core.server'),
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', cidrfield.models.IPNetworkField(validators=[hidlroute.core.models.should_be_single_IP])),
                ('server_member', models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT,
                                                    to='hidl_core.servertomember')),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('member_ptr',
                 models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True,
                                      primary_key=True, serialize=False, to='hidl_core.member')),
                (
                    'user',
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('hidl_core.member',),
        ),
        migrations.RunPython(insert_default_group),

    ]
