# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0043_auto_20150818_1726'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formazione',
            name='data_invio',
            field=models.DateTimeField(),
        ),
    ]
