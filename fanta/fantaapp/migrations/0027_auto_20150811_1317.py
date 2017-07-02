# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0026_auto_20150811_1314'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incontrocampionato',
            name='data',
            field=models.DateField(auto_now_add=True),
        ),
    ]
