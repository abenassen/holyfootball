# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('asta', '0009_offerta_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offerta',
            name='orario',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
