# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0014_campionato_totale_giornate'),
    ]

    operations = [
        migrations.AddField(
            model_name='giornata',
            name='disputata',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='lega',
            name='numero_gironi',
            field=models.PositiveIntegerField(default=4),
        ),
        migrations.AlterField(
            model_name='incontrolega',
            name='giornata',
            field=models.ForeignKey(blank=True, to='fantaapp.Giornata', null=True),
        ),
    ]
