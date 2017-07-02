# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0039_auto_20150815_1143'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='incontrolega',
            name='golcasa',
        ),
        migrations.RemoveField(
            model_name='incontrolega',
            name='goltrasferta',
        ),
        migrations.AddField(
            model_name='incontrolega',
            name='fmcasa',
            field=models.DecimalField(default=0.0, max_digits=5, decimal_places=2),
        ),
        migrations.AddField(
            model_name='incontrolega',
            name='fmtrasferta',
            field=models.DecimalField(default=0.0, max_digits=5, decimal_places=2),
        ),
    ]
