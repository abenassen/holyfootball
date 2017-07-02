# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0031_auto_20150811_2333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incontrocoppa',
            name='formazionecasa_andata',
            field=models.OneToOneField(related_name='FormazioneCoppaCasaAndata', null=True, blank=True, to='fantaapp.Formazione'),
        ),
        migrations.AlterField(
            model_name='incontrocoppa',
            name='formazionecasa_ritorno',
            field=models.OneToOneField(related_name='FormazioneCoppaCasaRitorno', null=True, blank=True, to='fantaapp.Formazione'),
        ),
        migrations.AlterField(
            model_name='incontrocoppa',
            name='formazionetrasferta_andata',
            field=models.OneToOneField(related_name='FormazioneCoppaTrasfertaAndata', null=True, blank=True, to='fantaapp.Formazione'),
        ),
        migrations.AlterField(
            model_name='incontrocoppa',
            name='formazionetrasferta_ritorno',
            field=models.OneToOneField(related_name='FormazioneCoppaTrasfertaRitorno', null=True, blank=True, to='fantaapp.Formazione'),
        ),
    ]
