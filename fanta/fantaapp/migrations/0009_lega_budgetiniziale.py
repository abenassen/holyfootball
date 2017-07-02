# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0008_auto_20150806_1909'),
    ]

    operations = [
        migrations.AddField(
            model_name='lega',
            name='budgetiniziale',
            field=models.PositiveIntegerField(default=1000),
        ),
    ]
