# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0017_auto_20150808_0952'),
    ]

    operations = [
        migrations.AlterField(
            model_name='giornatalega',
            name='giornata',
            field=models.ForeignKey(blank=True, to='fantaapp.Giornata', null=True),
        ),
    ]
