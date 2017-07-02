# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0012_auto_20150807_0823'),
    ]

    operations = [
        migrations.AddField(
            model_name='campionato',
            name='totale_giornate',
            field=models.PositiveIntegerField(default=38),
        ),
    ]
