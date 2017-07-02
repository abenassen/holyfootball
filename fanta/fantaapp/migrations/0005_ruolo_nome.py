# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0004_auto_20150806_0823'),
    ]

    operations = [
        migrations.AddField(
            model_name='ruolo',
            name='nome',
            field=models.CharField(default='D', max_length=5),
            preserve_default=False,
        ),
    ]
