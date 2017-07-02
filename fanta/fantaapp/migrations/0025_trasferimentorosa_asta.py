# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('asta', '0004_auto_20150810_1347'),
        ('fantaapp', '0024_auto_20150810_1327'),
    ]

    operations = [
        migrations.AddField(
            model_name='trasferimentorosa',
            name='asta',
            field=models.ForeignKey(blank=True, to='asta.Asta', null=True),
        ),
    ]
