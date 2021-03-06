# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-22 14:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Owner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('email', models.CharField(max_length=200)),
                ('pub_date', models.DateTimeField(verbose_name='date published')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('pub_date', models.DateTimeField(verbose_name='date published')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rafflie.Owner')),
            ],
        ),
        migrations.CreateModel(
            name='Raffle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('tickets', models.IntegerField(default=0)),
                ('pub_date', models.DateTimeField(verbose_name='date published')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rafflie.Owner')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rafflie.Product')),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pub_date', models.DateTimeField(verbose_name='date published')),
                ('raffle', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='rafflie.Raffle')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('email', models.CharField(max_length=200)),
                ('tickets', models.IntegerField(default=0)),
                ('pub_date', models.DateTimeField(verbose_name='date published')),
            ],
        ),
        migrations.AddField(
            model_name='ticket',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rafflie.User'),
        ),
        migrations.AddField(
            model_name='owner',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rafflie.User'),
        ),
    ]
