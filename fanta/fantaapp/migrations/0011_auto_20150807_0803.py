# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0010_auto_20150807_0003'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lega',
            name='numerogiocatori',
        ),
        migrations.AddField(
            model_name='lega',
            name='con_coppa',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='lega',
            name='numeroattaccanti',
            field=models.PositiveIntegerField(default=6),
        ),
        migrations.AddField(
            model_name='lega',
            name='numerocentrocampisti',
            field=models.PositiveIntegerField(default=8),
        ),
        migrations.AddField(
            model_name='lega',
            name='numerodifensori',
            field=models.PositiveIntegerField(default=8),
        ),
        migrations.AddField(
            model_name='lega',
            name='numeroportieri',
            field=models.PositiveIntegerField(default=3),
        ),
    ]
