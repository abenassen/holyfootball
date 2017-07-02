# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0022_auto_20150809_0938'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allenatore',
            name='amministratore',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='campionato',
            name='nome',
            field=models.CharField(unique=True, max_length=50),
        ),
    ]
