# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0020_auto_20150808_1445'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incontrocoppa',
            name='giornatalega_ritorno',
            field=models.ForeignKey(related_name='RitornoCoppa', blank=True, to='fantaapp.GiornataLega', null=True),
        ),
    ]
