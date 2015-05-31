# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields.hstore
from django.contrib.postgres.operations import HStoreExtension
from django.db import models, migrations

class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        x for x in [HStoreExtension()] if settings.PSQL_USER_IS_SUPERUSER] + [
        migrations.CreateModel(
            name='Relation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tags', django.contrib.postgres.fields.hstore.HStoreField()),
            ],
        ),
        migrations.CreateModel(
            name='Variant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tags', django.contrib.postgres.fields.hstore.HStoreField()),
            ],
        ),
        migrations.AddField(
            model_name='relation',
            name='variant',
            field=models.ForeignKey(to='gennotes_server.Variant'),
        ),
        migrations.RunSQL(
            'CREATE INDEX "gennotes_server_variant_tags_chrom_b37_idx" on ' +
            "gennotes_server_variant USING btree (( tags->'chrom_b37' )); " +
            'CREATE INDEX "gennotes_server_variant_tags_pos_b37_idx" on ' +
            "gennotes_server_variant USING btree (( tags->'pos_b37' ));"
            'CREATE INDEX "gennotes_server_variant_tags_ref_allele_b37_idx" on ' +
            "gennotes_server_variant USING btree (( tags->'ref_allele_b37' ));"
            'CREATE INDEX "gennotes_server_variant_tags_var_allele_b37_idx" on ' +
            "gennotes_server_variant USING btree (( tags->'var_allele_b37' ));"
            'CREATE INDEX "gennotes_server_relation_type_idx" on ' +
            "gennotes_server_relation USING btree (( tags->'type' ));"
        ),
    ]
