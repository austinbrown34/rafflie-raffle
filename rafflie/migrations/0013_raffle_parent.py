# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-28 09:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rafflie', '0012_winner'),
    ]

    operations = [
        migrations.AddField(
            model_name='raffle',
            name='parent',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
