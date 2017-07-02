# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0035_auto_20150813_1909'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='referto',
            options={'ordering': ['posizione']},
        ),
        migrations.AddField(
            model_name='referto',
            name='voto',
            field=models.ForeignKey(default=0, editable=False, to='fantaapp.Voto'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='voto',
            name='ha_giocato',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='formazione',
            name='definitiva',
            field=models.BooleanField(default=False),
        ),
    ]
