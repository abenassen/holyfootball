# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0032_auto_20150811_2335'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incontrocoppa',
            name='formazionecasa_andata',
            field=models.OneToOneField(related_name='IncontroCoppaCasaAndata', null=True, blank=True, to='fantaapp.Formazione'),
        ),
        migrations.AlterField(
            model_name='incontrocoppa',
            name='formazionecasa_ritorno',
            field=models.OneToOneField(related_name='IncontroCoppaCasaRitorno', null=True, blank=True, to='fantaapp.Formazione'),
        ),
        migrations.AlterField(
            model_name='incontrocoppa',
            name='formazionetrasferta_andata',
            field=models.OneToOneField(related_name='IncrontroCoppaTrasfertaAndata', null=True, blank=True, to='fantaapp.Formazione'),
        ),
        migrations.AlterField(
            model_name='incontrocoppa',
            name='formazionetrasferta_ritorno',
            field=models.OneToOneField(related_name='IncontroCoppaTrasfertaRitorno', null=True, blank=True, to='fantaapp.Formazione'),
        ),
        migrations.AlterField(
            model_name='incontrocoppa',
            name='incontrocasa',
            field=models.ForeignKey(related_name='QualificataCasaPer', blank=True, to='fantaapp.IncontroCoppa', null=True),
        ),
        migrations.AlterField(
            model_name='incontrocoppa',
            name='incontrotrasferta',
            field=models.ForeignKey(related_name='QualificataTrasfertaPer', blank=True, to='fantaapp.IncontroCoppa', null=True),
        ),
        migrations.AlterField(
            model_name='incontrolega',
            name='allenatorecasa',
            field=models.ForeignKey(related_name='IncontroCasa', to='fantaapp.Allenatore'),
        ),
        migrations.AlterField(
            model_name='incontrolega',
            name='allenatoretrasferta',
            field=models.ForeignKey(related_name='IncontroTrasferta', to='fantaapp.Allenatore'),
        ),
        migrations.AlterField(
            model_name='incontrolega',
            name='formazionecasa',
            field=models.OneToOneField(related_name='IncontroCasa', null=True, blank=True, to='fantaapp.Formazione'),
        ),
        migrations.AlterField(
            model_name='incontrolega',
            name='formazionetrasferta',
            field=models.OneToOneField(related_name='IncontroTrasferta', null=True, blank=True, to='fantaapp.Formazione'),
        ),
    ]
