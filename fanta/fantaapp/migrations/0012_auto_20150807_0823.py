# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0011_auto_20150807_0803'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='allenatore',
            name='numerogiocatori',
        ),
        migrations.AddField(
            model_name='allenatore',
            name='numeroattaccanti',
            field=models.PositiveIntegerField(default=6),
        ),
        migrations.AddField(
            model_name='allenatore',
            name='numerocentrocampisti',
            field=models.PositiveIntegerField(default=8),
        ),
        migrations.AddField(
            model_name='allenatore',
            name='numerodifensori',
            field=models.PositiveIntegerField(default=8),
        ),
        migrations.AddField(
            model_name='allenatore',
            name='numeroportieri',
            field=models.PositiveIntegerField(default=3),
        ),
    ]
