# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0015_auto_20150807_1532'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='incontrocalendario',
            name='allenatorecasa',
        ),
        migrations.RemoveField(
            model_name='incontrocalendario',
            name='allenatoretrasferta',
        ),
        migrations.RemoveField(
            model_name='incontrocalendario',
            name='lega',
        ),
        migrations.AddField(
            model_name='incontrolega',
            name='disputato',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='incontrolega',
            name='golcasa',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='incontrolega',
            name='goltrasferta',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='allenatore',
            unique_together=set([('utente', 'lega')]),
        ),
        migrations.DeleteModel(
            name='IncontroCalendario',
        ),
    ]
