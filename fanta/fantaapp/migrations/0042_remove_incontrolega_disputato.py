# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0041_referto_non_ha_giocato'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='incontrolega',
            name='disputato',
        ),
    ]
