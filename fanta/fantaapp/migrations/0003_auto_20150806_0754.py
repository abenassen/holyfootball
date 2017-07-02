# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0002_lega_codice'),
    ]

    operations = [
        migrations.RenameField(
            model_name='campionato',
            old_name='data_fine',
            new_name='datafine',
        ),
        migrations.RenameField(
            model_name='campionato',
            old_name='data_inizio',
            new_name='datainizio',
        ),
        migrations.AddField(
            model_name='calciatore',
            name='scorsoanno',
            field=models.ForeignKey(blank=True, to='fantaapp.Calciatore', null=True),
        ),
        migrations.AlterField(
            model_name='calciatore',
            name='ammonizioni',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='calciatore',
            name='assist',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='calciatore',
            name='espulsioni',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='calciatore',
            name='fantamedia',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='calciatore',
            name='fantamediasq',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='calciatore',
            name='golfatti',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='calciatore',
            name='golsubiti',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='calciatore',
            name='imageurl',
            field=models.URLField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='calciatore',
            name='mediavoto',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='calciatore',
            name='presenze',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='calciatore',
            name='quotazione',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='calciatore',
            name='rigoriparati',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
    ]
