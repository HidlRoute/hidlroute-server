# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-02-20 19:08

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

from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('easyaudit', '0007_auto_20180105_0838'),
    ]

    operations = [
        migrations.AddField(
            model_name='crudevent',
            name='changed_fields',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='crudevent',
            name='user_pk_as_string',
            field=models.CharField(blank=True, help_text='String version of the user pk', max_length=255, null=True),
        ),
    ]
