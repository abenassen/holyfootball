# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0036_auto_20150814_1751'),
    ]

    operations = [
        migrations.AddField(
            model_name='referto',
            name='entrato_in_campo',
            field=models.BooleanField(default=False),
        ),
    ]
