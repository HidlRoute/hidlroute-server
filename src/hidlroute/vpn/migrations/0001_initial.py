# Generated by Django 4.0.4 on 2022-05-27 16:57

import autoslug.fields
import django.contrib.postgres.indexes
from django.db import migrations, models
import django.db.models.deletion
import netfields.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("hidl_core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ServerToGroup",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("group", models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to="hidl_core.group")),
            ],
            options={
                "verbose_name": "Server Group",
                "verbose_name_plural": "Server Groups",
            },
        ),
        migrations.CreateModel(
            name="ServerToMember",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("member", models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to="hidl_core.member")),
            ],
            options={
                "verbose_name": "Server Member",
                "verbose_name_plural": "Server Members",
            },
        ),
        migrations.CreateModel(
            name="VpnServer",
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
                ("interface_name", models.CharField(max_length=16)),
                ("ip_address", netfields.fields.InetAddressField(max_length=39)),
                ("desired_state_raw", models.PositiveSmallIntegerField(db_column="desired_state", default=256)),
                ("state_change_job_id", models.CharField(blank=True, max_length=100, null=True)),
                ("state_change_job_msg", models.CharField(blank=True, max_length=100, null=True)),
                ("state_change_job_logs", models.TextField(blank=True, null=True)),
                ("state_change_job_start", models.DateTimeField(blank=True, null=True)),
                ("changes_made_ts", models.DateTimeField(blank=True, null=True)),
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
                ("subnet", models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to="hidl_core.subnet")),
            ],
            options={
                "verbose_name": "VPN Server",
                "verbose_name_plural": "VPN Servers",
            },
        ),
        migrations.CreateModel(
            name="VpnNetworkFilter",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("repr_cache", models.CharField(blank=True, max_length=200, null=True)),
                ("custom", models.CharField(blank=True, max_length=100, null=True)),
                (
                    "server_group",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="hidl_vpn.servertogroup"
                    ),
                ),
                (
                    "server_member",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="hidl_vpn.servertomember"
                    ),
                ),
                (
                    "subnet",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="network_from",
                        to="hidl_core.subnet",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="VpnFirewallRule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("comment", models.TextField(blank=True)),
                ("repr_cache", models.CharField(blank=True, max_length=200, null=True)),
                ("order", models.PositiveIntegerField(default=0)),
                ("action", models.CharField(max_length=20)),
                (
                    "network_from",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="network_from",
                        to="hidl_vpn.vpnnetworkfilter",
                        verbose_name="From",
                    ),
                ),
                (
                    "network_to",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="network_to",
                        to="hidl_vpn.vpnnetworkfilter",
                        verbose_name="To",
                    ),
                ),
                ("server", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="hidl_vpn.vpnserver")),
                (
                    "service",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        to="hidl_core.firewallservice",
                    ),
                ),
            ],
            options={
                "verbose_name": "Server Firewall Rule",
            },
        ),
        migrations.AddField(
            model_name="servertomember",
            name="server",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="hidl_vpn.vpnserver"),
        ),
        migrations.AddField(
            model_name="servertomember",
            name="subnet",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to="hidl_core.subnet"
            ),
        ),
        migrations.AddField(
            model_name="servertogroup",
            name="server",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="hidl_vpn.vpnserver"),
        ),
        migrations.AddField(
            model_name="servertogroup",
            name="subnet",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to="hidl_core.subnet"
            ),
        ),
        migrations.CreateModel(
            name="ServerRoutingRule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("comment", models.TextField(blank=True)),
                ("gateway", netfields.fields.InetAddressField(blank=True, max_length=39, null=True)),
                (
                    "interface",
                    models.CharField(
                        blank=True,
                        help_text="Use special keyword $self to reference interface of the VPN server this route is attached to",
                        max_length=16,
                        null=True,
                    ),
                ),
                (
                    "network",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="hidl_core.subnet"
                    ),
                ),
                (
                    "server",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="hidl_vpn.vpnserver"
                    ),
                ),
                (
                    "server_group",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="hidl_vpn.servertogroup"
                    ),
                ),
                (
                    "server_member",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="hidl_vpn.servertomember"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Device",
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
                ("ip_address", netfields.fields.InetAddressField(blank=True, max_length=39, unique=True)),
                ("mac_address", netfields.fields.MACAddressField(blank=True, null=True)),
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
                (
                    "server_to_member",
                    models.ForeignKey(
                        blank=True, on_delete=django.db.models.deletion.CASCADE, to="hidl_vpn.servertomember"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ClientRoutingRule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("comment", models.TextField(blank=True)),
                ("network", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="hidl_core.subnet")),
                (
                    "server",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="hidl_vpn.vpnserver"
                    ),
                ),
                (
                    "server_group",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="hidl_vpn.servertogroup"
                    ),
                ),
                (
                    "server_member",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="hidl_vpn.servertomember"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AlterUniqueTogether(
            name="servertomember",
            unique_together={("server", "member")},
        ),
        migrations.AlterUniqueTogether(
            name="servertogroup",
            unique_together={("server", "group")},
        ),
        migrations.CreateModel(
            name="IpAllocationMeta",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("last_allocated_ip", netfields.fields.InetAddressField(blank=True, max_length=39, null=True)),
                ("server", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="hidl_vpn.vpnserver")),
                ("subnet", models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to="hidl_core.subnet")),
            ],
            options={
                "unique_together": {("server", "subnet")},
            },
        ),
        migrations.AddIndex(
            model_name="device",
            index=django.contrib.postgres.indexes.GistIndex(
                fields=["ip_address"], name="hidl_device_ipaddress_idx", opclasses=("inet_ops",)
            ),
        ),
        migrations.AddConstraint(
            model_name="clientroutingrule",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(
                        ("server__isnull", True), ("server_group__isnull", False), ("server_member__isnull", True)
                    ),
                    models.Q(
                        ("server__isnull", True), ("server_group__isnull", True), ("server_member__isnull", False)
                    ),
                    models.Q(
                        ("server__isnull", False), ("server_group__isnull", True), ("server_member__isnull", True)
                    ),
                    _connector="OR",
                ),
                name="check_hidl_vpn_clientroutingrule_member_xor_group_xor_server",
            ),
        ),
    ]
