# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class FbUsers(models.Model):
    id_fb_users = models.AutoField(primary_key=True)
    id_fb = models.TextField()
    email = models.TextField()
    first_name = models.TextField()
    middle_name = models.TextField()
    last_name = models.TextField()
    gender = models.TextField()
    age = models.TextField()
    link_profile = models.TextField()
    timezone = models.TextField()
    token = models.TextField()
    location = models.TextField()
    last_day = models.DateTimeField()
    probs_location = models.TextField()
    mac = models.TextField(blank=True, null=True)
    node = models.TextField(blank=True, null=True)
    last_visit_mac = models.DateTimeField(blank=True, null=True)
    epoch = models.IntegerField(blank=True, null=True)
    fb_likes_count = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'Fb_Users'


class PageLikes(models.Model):
    id_page_likes = models.AutoField(primary_key=True)
    id_fb = models.TextField()
    token = models.TextField()
    page_name = models.TextField()
    page_id = models.TextField()
    category = models.TextField()
    created_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Page_likes'
