# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-10-16 13:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rafflie', '0023_ticket_entered'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='bundle',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='ticket',
            name='bundle_amount',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ticket',
            name='bundle_weight',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]