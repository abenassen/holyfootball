# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-24 12:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0060_auto_20160919_0048'),
    ]

    operations = [
        migrations.AddField(
            model_name='premiocompetizione',
            name='giornata',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='fantaapp.Giornata'),
        ),
    ]
