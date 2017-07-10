# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class Dbversion(models.Model):
    id = models.IntegerField(primary_key=True)
    db_version = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'dbversion'


class DepModes(models.Model):
    mode_id = models.IntegerField(primary_key=True)
    mode = models.CharField(max_length=25)

    class Meta:
        managed = False
        db_table = 'dep_modes'


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class EventTable(models.Model):
    event_type = models.CharField(max_length=30)
    target = models.CharField(max_length=255)
    host = models.CharField(max_length=30)
    update_flag = models.IntegerField()
    condition_met = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'event_table'


class Jobs(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    host = models.CharField(max_length=30)
    user = models.CharField(max_length=31)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    depends = models.IntegerField(default = 0, )
    depend_mode = models.IntegerField(default = 0, blank=True, null=True)
    event_trigger = models.IntegerField(default = 0)
    reoccur = models.CharField(max_length=30, blank=True, null=True)
    status = models.IntegerField(default = 99999)
    rc = models.IntegerField(default = 99999, blank=True, null=True)
    command = models.CharField(max_length=300, null=True)
    update_flag = models.IntegerField(default = 1)
    comment = models.TextField()
    log_retention = models.IntegerField(default = 30)
    pid = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'jobs'
        unique_together = (('name', 'host'),)


class Results(models.Model):
    id = models.IntegerField(primary_key=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    output = models.TextField(blank=True, null=True)
    uid = models.CharField(max_length=32)
    rc = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'results'
