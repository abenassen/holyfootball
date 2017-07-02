# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0044_auto_20150822_0326'),
    ]

    operations = [
        migrations.RenameField(
            model_name='incontrolega',
            old_name='fmcasa',
            new_name='fmcasa_nomod',
        ),
        migrations.RenameField(
            model_name='incontrolega',
            old_name='fmtrasferta',
            new_name='fmtrasferta_nomod',
        ),
        migrations.AddField(
            model_name='incontrolega',
            name='modcasa',
            field=models.DecimalField(default=0.0, max_digits=5, decimal_places=2),
        ),
        migrations.AddField(
            model_name='incontrolega',
            name='modtrasferta',
            field=models.DecimalField(default=0.0, max_digits=5, decimal_places=2),
        ),
    ]
