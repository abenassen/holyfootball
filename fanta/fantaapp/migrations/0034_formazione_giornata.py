# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0033_auto_20150811_2341'),
    ]

    operations = [
        migrations.AddField(
            model_name='formazione',
            name='giornata',
            field=models.ForeignKey(default=0, to='fantaapp.Giornata'),
            preserve_default=False,
        ),
    ]
