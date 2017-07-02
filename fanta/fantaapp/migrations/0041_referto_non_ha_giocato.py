# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0040_auto_20150816_1304'),
    ]

    operations = [
        migrations.AddField(
            model_name='referto',
            name='non_ha_giocato',
            field=models.BooleanField(default=False),
        ),
    ]
