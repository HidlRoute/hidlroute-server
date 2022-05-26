# Generated by Django 4.0.4 on 2022-05-26 19:26

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

from django.db import migrations, models
import django.db.models.deletion
import hidlroute.contrib.wireguard.service.key


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("hidl_vpn", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="WireguardPeer",
            fields=[
                (
                    "device_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="hidl_vpn.device",
                    ),
                ),
                ("public_key", models.CharField(max_length=1024)),
            ],
            options={
                "abstract": False,
            },
            bases=("hidl_vpn.device",),
        ),
        migrations.CreateModel(
            name="WireguardServer",
            fields=[
                (
                    "vpnserver_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="hidl_vpn.vpnserver",
                    ),
                ),
                (
                    "private_key",
                    models.CharField(
                        default=hidlroute.contrib.wireguard.service.key.generate_private_key, max_length=1024
                    ),
                ),
                ("listen_port", models.IntegerField(default=5762)),
                ("preshared_key", models.CharField(blank=True, max_length=1024, null=True)),
                (
                    "client_dns",
                    models.CharField(
                        blank=True, help_text="DNS to be pushed to client configs", max_length=1024, null=True
                    ),
                ),
                (
                    "client_keep_alive",
                    models.IntegerField(blank=True, help_text="Keep alive options to be pushed to clients", null=True),
                ),
                (
                    "client_endpoint",
                    models.CharField(
                        help_text="Public server hostname or IP to be pushed to the client. \nOptionally you could set port in a form of HOST:PORT to override port for the client.",
                        max_length=1024,
                    ),
                ),
            ],
            options={
                "verbose_name": "Wireguard Server",
            },
            bases=("hidl_vpn.vpnserver",),
        ),
    ]
