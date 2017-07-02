# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0038_auto_20150814_1853'),
    ]

    operations = [
        migrations.AddField(
            model_name='referto',
            name='da_ricalcolare',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='referto',
            name='modificatore',
            field=models.BooleanField(default=False),
        ),
    ]
