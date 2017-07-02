# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0007_auto_20150806_1842'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lega',
            name='descrizione',
            field=models.TextField(blank=True),
        ),
    ]
