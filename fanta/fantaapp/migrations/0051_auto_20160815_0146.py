# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-14 23:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


def cambia_incontri(apps, schema_editor):
    IncontroLega = apps.get_model("fantaapp", "IncontroLega")
    for inc in IncontroLega.objects.all():
	inc.giornata = inc.giornatalega.giornata
	inc.save()



class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0050_auto_20160814_1439'),
    ]

    operations = [
        migrations.AddField(
            model_name='incontrolega',
            name='giornata',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='fantaapp.Giornata'),
            preserve_default=False,
        ),
	migrations.RunPython(cambia_incontri),
        migrations.RemoveField(
            model_name='incontrolega',
            name='giornatalega',
        ),

    ]
