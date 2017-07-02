# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import fantaapp.models
import fantaapp.models.auxfun

class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lega',
            name='codice',
            field=models.CharField(default=fantaapp.models.auxfun.randomHash, unique=True, max_length=20),
        ),
    ]
