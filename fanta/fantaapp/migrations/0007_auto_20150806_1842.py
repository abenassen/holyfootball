# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0006_auto_20150806_1841'),
    ]

    operations = [
        migrations.RenameField(
            model_name='lega',
            old_name='numeroparteciparti',
            new_name='numeropartecipanti',
        ),
    ]
