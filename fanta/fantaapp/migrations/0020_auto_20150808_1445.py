# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0019_allenatore_logourl'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='incontrocoppa',
            name='formazionecasa',
        ),
        migrations.RemoveField(
            model_name='incontrocoppa',
            name='formazionetrasferta',
        ),
        migrations.RemoveField(
            model_name='incontrocoppa',
            name='giornata',
        ),
        migrations.RemoveField(
            model_name='incontrocoppa',
            name='giornatalega',
        ),
        migrations.AddField(
            model_name='incontrocoppa',
            name='andata_ritorno',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='incontrocoppa',
            name='formazionecasa_andata',
            field=models.ForeignKey(related_name='FormazioneCoppaCasaAndata', blank=True, to='fantaapp.Formazione', null=True),
        ),
        migrations.AddField(
            model_name='incontrocoppa',
            name='formazionecasa_ritorno',
            field=models.ForeignKey(related_name='FormazioneCoppaCasaRitorno', blank=True, to='fantaapp.Formazione', null=True),
        ),
        migrations.AddField(
            model_name='incontrocoppa',
            name='formazionetrasferta_andata',
            field=models.ForeignKey(related_name='FormazioneCoppaTrasfertaAndata', blank=True, to='fantaapp.Formazione', null=True),
        ),
        migrations.AddField(
            model_name='incontrocoppa',
            name='formazionetrasferta_ritorno',
            field=models.ForeignKey(related_name='FormazioneCoppaTrasfertaRitorno', blank=True, to='fantaapp.Formazione', null=True),
        ),
        migrations.AddField(
            model_name='incontrocoppa',
            name='giornatalega_andata',
            field=models.ForeignKey(related_name='AndataCoppa', default=0, to='fantaapp.GiornataLega'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='incontrocoppa',
            name='giornatalega_ritorno',
            field=models.ForeignKey(related_name='RitornoCoppa', default=0, to='fantaapp.GiornataLega'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='incontrocoppa',
            name='tipo',
            field=models.CharField(default=b'Turno Preliminare', max_length=20),
        ),
    ]
