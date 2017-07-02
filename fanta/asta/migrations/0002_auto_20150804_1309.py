# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('asta', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calciatorechiamato',
            name='calciatore',
            field=models.ForeignKey(to='fantaapp.Calciatore'),
        ),
        migrations.AlterField(
            model_name='confrontocalciatori',
            name='calciatore1',
            field=models.ForeignKey(related_name='Calc1', to='fantaapp.Calciatore'),
        ),
        migrations.AlterField(
            model_name='confrontocalciatori',
            name='calciatore2',
            field=models.ForeignKey(related_name='Calc2', to='fantaapp.Calciatore'),
        ),
        migrations.AlterField(
            model_name='offerta',
            name='allenatore',
            field=models.ForeignKey(to='fantaapp.Allenatore'),
        ),
        migrations.AlterField(
            model_name='offerta',
            name='calciatore',
            field=models.ForeignKey(to='fantaapp.Calciatore'),
        ),
        migrations.DeleteModel(
            name='Allenatore',
        ),
        migrations.DeleteModel(
            name='Calciatore',
        ),
    ]
