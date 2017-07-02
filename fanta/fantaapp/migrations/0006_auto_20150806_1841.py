# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0005_ruolo_nome'),
    ]

    operations = [
        migrations.AddField(
            model_name='lega',
            name='numeroparteciparti',
            field=models.PositiveIntegerField(default=10, validators=[django.core.validators.MaxValueValidator(20)]),
        ),
        migrations.AlterField(
            model_name='lega',
            name='calcolo_voto',
            field=models.CharField(default=b'votostd', max_length=100),
        ),
    ]
