# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0045_auto_20150921_2110'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='incontrocoppa',
            name='allenatorecasa',
        ),
        migrations.RemoveField(
            model_name='incontrocoppa',
            name='allenatoretrasferta',
        ),
        migrations.RemoveField(
            model_name='incontrocoppa',
            name='disputato',
        ),
        migrations.RemoveField(
            model_name='incontrocoppa',
            name='formazionecasa_andata',
        ),
        migrations.RemoveField(
            model_name='incontrocoppa',
            name='formazionecasa_ritorno',
        ),
        migrations.RemoveField(
            model_name='incontrocoppa',
            name='formazionetrasferta_andata',
        ),
        migrations.RemoveField(
            model_name='incontrocoppa',
            name='formazionetrasferta_ritorno',
        ),
        migrations.RemoveField(
            model_name='incontrocoppa',
            name='giornatalega_andata',
        ),
        migrations.RemoveField(
            model_name='incontrocoppa',
            name='giornatalega_ritorno',
        ),
        migrations.RemoveField(
            model_name='incontrocoppa',
            name='golcasa',
        ),
        migrations.RemoveField(
            model_name='incontrocoppa',
            name='goltrasferta',
        ),
        migrations.AddField(
            model_name='incontrocoppa',
            name='incontro_andata',
            field=models.OneToOneField(related_name='IncontroCoppaAnd', null=True, blank=True, to='fantaapp.IncontroLega'),
        ),
        migrations.AddField(
            model_name='incontrocoppa',
            name='incontro_ritorno',
            field=models.OneToOneField(related_name='IncontroCoppaRit', null=True, blank=True, to='fantaapp.IncontroLega'),
        ),
        migrations.AlterField(
            model_name='incontrolega',
            name='allenatorecasa',
            field=models.ForeignKey(related_name='IncontroCasa', blank=True, to='fantaapp.Allenatore', null=True),
        ),
        migrations.AlterField(
            model_name='incontrolega',
            name='allenatoretrasferta',
            field=models.ForeignKey(related_name='IncontroTrasferta', blank=True, to='fantaapp.Allenatore', null=True),
        ),
        migrations.AlterField(
            model_name='incontrolega',
            name='lega',
            field=models.ForeignKey(blank=True, to='fantaapp.Lega', null=True),
        ),
    ]
