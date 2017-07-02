# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0023_auto_20150809_1530'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrasferimentoRosa',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('valore', models.PositiveSmallIntegerField()),
                ('acquisto', models.BooleanField(default=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='transferlega',
            name='allenatore',
        ),
        migrations.RemoveField(
            model_name='transferlega',
            name='calciatore',
        ),
        migrations.AlterField(
            model_name='allenatore',
            name='budget',
            field=models.PositiveSmallIntegerField(editable=False, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='allenatore',
            name='numeroattaccanti',
            field=models.PositiveIntegerField(editable=False, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='allenatore',
            name='numerocentrocampisti',
            field=models.PositiveIntegerField(editable=False, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='allenatore',
            name='numerodifensori',
            field=models.PositiveIntegerField(editable=False, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='allenatore',
            name='numeroportieri',
            field=models.PositiveIntegerField(editable=False, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.DeleteModel(
            name='TransferLega',
        ),
        migrations.AddField(
            model_name='trasferimentorosa',
            name='allenatore',
            field=models.ForeignKey(to='fantaapp.Allenatore'),
        ),
        migrations.AddField(
            model_name='trasferimentorosa',
            name='calciatore',
            field=models.ForeignKey(to='fantaapp.Calciatore'),
        ),
    ]
