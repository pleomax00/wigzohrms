# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-27 11:44
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20160427_1112'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='actualdob',
            field=models.DateField(default=datetime.date(2015, 1, 1)),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='documenteddob',
            field=models.DateField(default=datetime.date(2015, 1, 1)),
        ),
    ]
