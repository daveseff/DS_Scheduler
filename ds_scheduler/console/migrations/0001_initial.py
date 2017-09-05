# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-11 01:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Dbversion',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('db_version', models.IntegerField()),
            ],
            options={
                'db_table': 'dbversion',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DepModes',
            fields=[
                ('mode_id', models.IntegerField(primary_key=True, serialize=False)),
                ('mode', models.CharField(max_length=25)),
            ],
            options={
                'db_table': 'dep_modes',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DjangoMigrations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('applied', models.DateTimeField()),
            ],
            options={
                'db_table': 'django_migrations',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='EventTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(max_length=30)),
                ('target', models.CharField(max_length=255)),
                ('host', models.CharField(max_length=30)),
                ('update_flag', models.IntegerField()),
                ('condition_met', models.IntegerField()),
            ],
            options={
                'db_table': 'event_table',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Jobs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('host', models.CharField(max_length=30)),
                ('user', models.CharField(max_length=31)),
                ('start_time', models.DateTimeField(blank=True, null=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('depends', models.IntegerField()),
                ('depend_mode', models.IntegerField()),
                ('event_trigger', models.IntegerField()),
                ('reoccur', models.CharField(blank=True, max_length=30, null=True)),
                ('status', models.IntegerField()),
                ('rc', models.IntegerField(blank=True, null=True)),
                ('command', models.CharField(max_length=300)),
                ('update_flag', models.IntegerField()),
                ('comment', models.TextField()),
                ('log_retention', models.IntegerField()),
                ('pid', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'jobs',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Results',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('start_date', models.DateTimeField(blank=True, null=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('output', models.TextField(blank=True, null=True)),
                ('uid', models.CharField(max_length=32)),
                ('rc', models.IntegerField()),
            ],
            options={
                'db_table': 'results',
                'managed': False,
            },
        ),
    ]