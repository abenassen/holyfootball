# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('asta', '0008_offerta_calciatore_da_lasciare'),
    ]

    operations = [
        migrations.AddField(
            model_name='offerta',
            name='status',
            field=models.CharField(default=b'attiva', max_length=10),
        ),
    ]
