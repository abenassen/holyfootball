# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0034_formazione_giornata'),
    ]

    operations = [
        migrations.AddField(
            model_name='formazione',
            name='modulo',
            field=models.CommaSeparatedIntegerField(default=b'4,4,2', max_length=5),
        ),
        migrations.AddField(
            model_name='referto',
            name='fantavoto',
            field=models.DecimalField(null=True, max_digits=4, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='referto',
            name='votopuro',
            field=models.DecimalField(null=True, max_digits=4, decimal_places=2, blank=True),
        ),
    ]
