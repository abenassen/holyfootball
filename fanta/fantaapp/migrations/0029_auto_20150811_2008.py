# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0028_auto_20150811_1325'),
    ]

    operations = [
        migrations.AddField(
            model_name='voto',
            name='calciatore',
            field=models.ForeignKey(default=0, to='fantaapp.Calciatore'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='voto',
            name='goldellavittoria',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='voto',
            name='goldelpareggio',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='voto',
            name='rigoriparati',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='voto',
            name='rigorisbagliati',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=False,
        ),
    ]
