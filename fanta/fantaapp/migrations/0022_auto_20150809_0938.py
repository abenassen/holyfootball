# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import fantaapp.models
import fantaapp.models.auxfun


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0021_auto_20150808_1507'),
    ]

    operations = [
        migrations.AddField(
            model_name='incontrocoppa',
            name='indice',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='lega',
            name='codice',
            field=models.CharField(default=fantaapp.models.auxfun.randomHash, unique=True, max_length=20, db_index=True),
        ),
        migrations.AlterUniqueTogether(
            name='incontrocoppa',
            unique_together=set([('lega', 'indice', 'tipo')]),
        ),
    ]
