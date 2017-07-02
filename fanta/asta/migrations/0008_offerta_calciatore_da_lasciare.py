# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0044_auto_20150822_0326'),
        ('asta', '0007_remove_asta_iniziale'),
    ]

    operations = [
        migrations.AddField(
            model_name='offerta',
            name='calciatore_da_lasciare',
            field=models.ForeignKey(related_name='LasciatiIn', blank=True, to='fantaapp.Calciatore', null=True),
        ),
    ]
