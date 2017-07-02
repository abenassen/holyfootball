# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0037_referto_entrato_in_campo'),
    ]

    operations = [
        migrations.RenameField(
            model_name='referto',
            old_name='fantavoto',
            new_name='fantavoto_db',
        ),
        migrations.RenameField(
            model_name='referto',
            old_name='votopuro',
            new_name='votopuro_db',
        ),
    ]
