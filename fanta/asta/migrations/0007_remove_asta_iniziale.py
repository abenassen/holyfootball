# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('asta', '0006_auto_20150905_2204'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='asta',
            name='iniziale',
        ),
    ]
