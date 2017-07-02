# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Acquisto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Allenatore',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=40)),
                ('budjet', models.PositiveSmallIntegerField()),
                ('numero_giocatori', models.CommaSeparatedIntegerField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Calciatore',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=40)),
                ('ruolo', models.PositiveSmallIntegerField(choices=[(b'p', 0), (b'd', 1), (b'c', 2), (b'a', 3)])),
                ('squadra', models.CharField(max_length=40)),
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
            name='CalciatoreChiamato',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('calciatore', models.ForeignKey(to='asta.Calciatore')),
            ],
        ),
        migrations.CreateModel(
            name='ConfrontoCalciatori',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('calciatore1', models.ForeignKey(related_name='Calc1', to='asta.Calciatore')),
                ('calciatore2', models.ForeignKey(related_name='Calc2', to='asta.Calciatore')),
            ],
        ),
        migrations.CreateModel(
            name='Offerta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('soldi', models.PositiveSmallIntegerField()),
                ('orario', models.DateTimeField()),
                ('allenatore', models.ForeignKey(to='asta.Allenatore')),
                ('calciatore', models.ForeignKey(to='asta.Calciatore')),
            ],
        ),
        migrations.AddField(
            model_name='acquisto',
            name='offerta',
            field=models.ForeignKey(to='asta.Offerta'),
        ),
    ]
