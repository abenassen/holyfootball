# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-19 23:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0055_auto_20160820_0104'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='incontrolega',
            name='competizione',
        ),
        migrations.AddField(
            model_name='incontrocoppa',
            name='faseoriginale',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='faseoriginalecoppa', to='fantaapp.FaseCompetizione'),
        ),
        migrations.AddField(
            model_name='incontrolega',
            name='faseoriginale',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='faseoriginale', to='fantaapp.FaseCompetizione'),
        ),
        migrations.AlterField(
            model_name='incontrocoppa',
            name='fase',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='fantaapp.FaseCompetizione'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='incontrocoppa',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='incontrocoppa',
            name='competizione',
        ),
        migrations.RemoveField(
            model_name='incontrocoppa',
            name='indice',
        ),
        migrations.RemoveField(
            model_name='incontrocoppa',
            name='tipo',
        ),
    ]
