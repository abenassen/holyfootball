# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0025_trasferimentorosa_asta'),
    ]

    operations = [
        migrations.AddField(
            model_name='incontrocampionato',
            name='disputato',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='incontrocampionato',
            name='golcasa',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='incontrocampionato',
            name='goltrasferta',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='giornata',
            name='data',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='giornata',
            name='disputata',
            field=models.BooleanField(default=False),
        ),
    ]
