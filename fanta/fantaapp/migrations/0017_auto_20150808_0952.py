# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0016_auto_20150807_1908'),
    ]

    operations = [
        migrations.CreateModel(
            name='GiornataLega',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('numero', models.PositiveSmallIntegerField()),
                ('giornata', models.ForeignKey(to='fantaapp.Giornata')),
                ('lega', models.ForeignKey(to='fantaapp.Lega')),
            ],
        ),
        migrations.CreateModel(
            name='IncontroCoppa',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('giornatalega', models.PositiveSmallIntegerField()),
                ('golcasa', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('goltrasferta', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('disputato', models.BooleanField(default=False)),
                ('allenatorecasa', models.ForeignKey(related_name='AllenatoreCoppaCasa', blank=True, to='fantaapp.Allenatore', null=True)),
                ('allenatoretrasferta', models.ForeignKey(related_name='AllenatoreCoppaTrasferta', blank=True, to='fantaapp.Allenatore', null=True)),
                ('formazionecasa', models.ForeignKey(related_name='FormazioneCoppaCasa', blank=True, to='fantaapp.Formazione', null=True)),
                ('formazionetrasferta', models.ForeignKey(related_name='FormazioneCoppaTrasferta', blank=True, to='fantaapp.Formazione', null=True)),
                ('giornata', models.ForeignKey(blank=True, to='fantaapp.Giornata', null=True)),
                ('incontrocasa', models.ForeignKey(related_name='IncontroCoppaCasa', blank=True, to='fantaapp.IncontroCoppa', null=True)),
                ('incontrotrasferta', models.ForeignKey(related_name='IncontroCoppaTrasferta', blank=True, to='fantaapp.IncontroCoppa', null=True)),
                ('lega', models.ForeignKey(to='fantaapp.Lega')),
            ],
        ),
        migrations.RemoveField(
            model_name='incontrolega',
            name='giornata',
        ),
        migrations.AlterField(
            model_name='incontrolega',
            name='formazionecasa',
            field=models.ForeignKey(related_name='FormazioneCasa', blank=True, to='fantaapp.Formazione', null=True),
        ),
        migrations.AlterField(
            model_name='incontrolega',
            name='formazionetrasferta',
            field=models.ForeignKey(related_name='FormazioneTrasferta', blank=True, to='fantaapp.Formazione', null=True),
        ),
        migrations.AlterField(
            model_name='incontrolega',
            name='giornatalega',
            field=models.ForeignKey(to='fantaapp.GiornataLega'),
        ),
    ]
