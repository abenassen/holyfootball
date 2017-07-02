# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0027_auto_20150811_1317'),
    ]

    operations = [
        migrations.AlterField(
            model_name='giornata',
            name='data',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='incontrocampionato',
            name='data',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
