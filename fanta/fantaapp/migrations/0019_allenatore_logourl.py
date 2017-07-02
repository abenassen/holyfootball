# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0018_auto_20150808_0956'),
    ]

    operations = [
        migrations.AddField(
            model_name='allenatore',
            name='logourl',
            field=models.URLField(default=b'/static/fantaapp/images/savona.png'),
        ),
    ]
