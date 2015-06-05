# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.db import migrations


def add_clinvar_bot_users(apps, schema_editor):
    usernames = ['clinvar-variant-importer', 'clinvar-data-importer']
    for username in usernames:
        get_user_model().objects.get_or_create(username=username)


class Migration(migrations.Migration):

    dependencies = [
        ('gennotes_server', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_clinvar_bot_users),
    ]
