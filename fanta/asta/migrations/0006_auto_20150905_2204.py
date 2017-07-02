# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('asta', '0005_auto_20150811_1314'),
    ]

    operations = [
        migrations.AddField(
            model_name='asta',
            name='apertura',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 5, 20, 4, 3, 282477, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='asta',
            name='chiusura',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 5, 20, 4, 20, 794903, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='asta',
            name='tipo',
            field=models.CharField(default=b'random', max_length=10),
        ),
    ]
