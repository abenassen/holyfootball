# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0047_messaggio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messaggio',
            name='data',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
