# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-10-16 12:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rafflie', '0022_auto_20171015_2348'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='entered',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]