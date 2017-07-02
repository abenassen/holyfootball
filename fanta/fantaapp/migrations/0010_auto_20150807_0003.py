# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0009_lega_budgetiniziale'),
    ]

    operations = [
        migrations.AddField(
            model_name='lega',
            name='numerogiocatori',
            field=models.PositiveIntegerField(default=25),
        ),
        migrations.AddField(
            model_name='lega',
            name='redazione',
            field=models.ForeignKey(default=0, to='fantaapp.Redazione'),
            preserve_default=False,
        ),
    ]
