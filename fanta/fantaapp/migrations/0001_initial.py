# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Allenatore',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('budget', models.PositiveSmallIntegerField()),
                ('numerogiocatori', models.CommaSeparatedIntegerField(max_length=20)),
                ('nomesquadra', models.CharField(max_length=200)),
                ('amministratore', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Calciatore',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=40)),
                ('ruolo', models.PositiveSmallIntegerField(choices=[(b'p', 0), (b'd', 1), (b'c', 2), (b'a', 3)])),
                ('exsquadra', models.CharField(max_length=40)),
                ('quotazione', models.PositiveSmallIntegerField()),
                ('fantamedia', models.FloatField()),
                ('fantamediasq', models.FloatField()),
                ('mediavoto', models.FloatField()),
                ('presenze', models.PositiveSmallIntegerField()),
                ('golfatti', models.PositiveSmallIntegerField()),
                ('golsubiti', models.PositiveSmallIntegerField()),
                ('rigoriparati', models.PositiveSmallIntegerField()),
                ('ammonizioni', models.PositiveSmallIntegerField()),
                ('espulsioni', models.PositiveSmallIntegerField()),
                ('assist', models.PositiveSmallIntegerField()),
                ('imageurl', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='Campionato',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=50)),
                ('data_inizio', models.DateField()),
                ('data_fine', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Formazione',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_invio', models.DateField()),
                ('definitiva', models.BooleanField()),
                ('allenatore', models.ForeignKey(to='fantaapp.Allenatore')),
            ],
        ),
        migrations.CreateModel(
            name='Giornata',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('numero', models.PositiveSmallIntegerField()),
                ('data', models.DateField()),
                ('campionato', models.ForeignKey(to='fantaapp.Campionato')),
            ],
        ),
        migrations.CreateModel(
            name='IncontroCalendario',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('giornata', models.PositiveSmallIntegerField()),
                ('allenatorecasa', models.ForeignKey(related_name='incontricasa', to='fantaapp.Allenatore')),
                ('allenatoretrasferta', models.ForeignKey(related_name='incontritrasferta', to='fantaapp.Allenatore')),
            ],
        ),
        migrations.CreateModel(
            name='IncontroCampionato',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', models.DateField()),
                ('giornata', models.ForeignKey(to='fantaapp.Giornata')),
            ],
        ),
        migrations.CreateModel(
            name='IncontroLega',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('giornatalega', models.PositiveSmallIntegerField()),
                ('formazionecasa', models.ForeignKey(related_name='IncontroCasa', to='fantaapp.Formazione')),
                ('formazionetrasferta', models.ForeignKey(related_name='IncontroTrasferta', to='fantaapp.Formazione')),
                ('giornata', models.ForeignKey(to='fantaapp.Giornata')),
            ],
        ),
        migrations.CreateModel(
            name='Lega',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=50)),
                ('descrizione', models.TextField()),
                ('calcolo_voto', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Redazione',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=50)),
                ('descrizione', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Referto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('posizione', models.PositiveSmallIntegerField()),
                ('calciatore', models.ForeignKey(to='fantaapp.Calciatore')),
                ('formazione', models.ForeignKey(to='fantaapp.Formazione')),
            ],
        ),
        migrations.CreateModel(
            name='SquadraCampionato',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=50)),
                ('campionato', models.ForeignKey(to='fantaapp.Campionato')),
            ],
        ),
        migrations.CreateModel(
            name='TransferLega',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('costo', models.PositiveSmallIntegerField()),
                ('entrata', models.BooleanField()),
                ('allenatore', models.ForeignKey(to='fantaapp.Allenatore')),
                ('calciatore', models.ForeignKey(to='fantaapp.Calciatore')),
            ],
        ),
        migrations.CreateModel(
            name='Voto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('votopuro', models.DecimalField(max_digits=4, decimal_places=2)),
                ('assist', models.PositiveSmallIntegerField()),
                ('golsuazione', models.PositiveSmallIntegerField()),
                ('golsurigore', models.PositiveSmallIntegerField()),
                ('ammo', models.PositiveSmallIntegerField()),
                ('espu', models.PositiveSmallIntegerField()),
                ('autogol', models.PositiveSmallIntegerField()),
                ('golsubiti', models.PositiveSmallIntegerField()),
                ('giornata', models.ForeignKey(to='fantaapp.Giornata')),
                ('redazione', models.ForeignKey(to='fantaapp.Redazione')),
            ],
        ),
        migrations.AddField(
            model_name='incontrolega',
            name='lega',
            field=models.ForeignKey(to='fantaapp.Lega'),
        ),
        migrations.AddField(
            model_name='incontrocampionato',
            name='squadracasa',
            field=models.ForeignKey(related_name='IncontroCasa', to='fantaapp.SquadraCampionato'),
        ),
        migrations.AddField(
            model_name='incontrocampionato',
            name='squadratrasferta',
            field=models.ForeignKey(related_name='IncontroTransferta', to='fantaapp.SquadraCampionato'),
        ),
        migrations.AddField(
            model_name='incontrocalendario',
            name='lega',
            field=models.ForeignKey(to='fantaapp.Lega'),
        ),
        migrations.AddField(
            model_name='formazione',
            name='giocatori',
            field=models.ManyToManyField(to='fantaapp.Calciatore', through='fantaapp.Referto'),
        ),
        migrations.AddField(
            model_name='calciatore',
            name='squadra',
            field=models.ForeignKey(to='fantaapp.SquadraCampionato'),
        ),
        migrations.AddField(
            model_name='allenatore',
            name='lega',
            field=models.ForeignKey(to='fantaapp.Lega'),
        ),
        migrations.AddField(
            model_name='allenatore',
            name='utente',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
