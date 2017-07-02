# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('asta', '0003_auto_20150809_1530'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='acquisto',
            name='offerta',
        ),
        migrations.DeleteModel(
            name='Acquisto',
        ),
    ]
