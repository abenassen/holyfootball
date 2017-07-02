# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0042_remove_incontrolega_disputato'),
    ]

    operations = [
        migrations.AddField(
            model_name='calciatore',
            name='primavera',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='calciatore',
            name='squadra',
            field=models.ForeignKey(blank=True, to='fantaapp.SquadraCampionato', null=True),
        ),
        migrations.AlterField(
            model_name='referto',
            name='voto',
            field=models.ForeignKey(blank=True, to='fantaapp.Voto', null=True),
        ),
    ]
