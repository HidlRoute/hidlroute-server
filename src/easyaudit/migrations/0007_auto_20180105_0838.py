# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-05 08:38

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
        ('easyaudit', '0006_auto_20171018_1242'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crudevent',
            name='event_type',
            field=models.SmallIntegerField(choices=[(1, 'Create'), (2, 'Update'), (3, 'Delete'), (4, 'Many-to-Many Change'), (5, 'Reverse Many-to-Many Change')]),
        ),
        migrations.AlterField(
            model_name='crudevent',
            name='user_pk_as_string',
            field=models.CharField(blank=True, help_text='String version of the user pk', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='loginevent',
            name='login_type',
            field=models.SmallIntegerField(choices=[(0, 'Login'), (1, 'Logout'), (2, 'Failed login')]),
        ),
    ]