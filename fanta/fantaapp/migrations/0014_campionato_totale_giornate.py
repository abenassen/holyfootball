# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import fantaapp.models


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0013_auto_20150807_1454'),
    ]

    operations = [
        migrations.AddField(
            model_name='incontrolega',
            name='allenatorecasa',
            field=models.ForeignKey(related_name='AllenatoreCasa', default=0, to='fantaapp.Allenatore'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='incontrolega',
            name='allenatoretrasferta',
            field=models.ForeignKey(related_name='AllenatoreTrasferta', default=0, to='fantaapp.Allenatore'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lega',
            name='campionato',
            field=models.ForeignKey(default=fantaapp.models.campionatoreale.Campionato.lastCampionato, to='fantaapp.Campionato'),
        ),
        migrations.AlterField(
            model_name='incontrolega',
            name='formazionecasa',
            field=models.ForeignKey(related_name='IncontroCasa', blank=True, to='fantaapp.Formazione', null=True),
        ),
        migrations.AlterField(
            model_name='incontrolega',
            name='formazionetrasferta',
            field=models.ForeignKey(related_name='IncontroTrasferta', blank=True, to='fantaapp.Formazione', null=True),
        ),
    ]
