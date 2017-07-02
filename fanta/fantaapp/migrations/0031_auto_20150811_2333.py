# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0030_auto_20150811_2011'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incontrolega',
            name='formazionecasa',
            field=models.OneToOneField(related_name='FormazioneCasa', null=True, blank=True, to='fantaapp.Formazione'),
        ),
        migrations.AlterField(
            model_name='incontrolega',
            name='formazionetrasferta',
            field=models.OneToOneField(related_name='FormazioneTrasferta', null=True, blank=True, to='fantaapp.Formazione'),
        ),
    ]
