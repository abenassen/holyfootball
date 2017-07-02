# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0003_auto_20150806_0754'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ruolo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='calciatore',
            name='ruolo',
        ),
        migrations.AddField(
            model_name='ruolo',
            name='calciatore',
            field=models.ForeignKey(related_name='ruolo', to='fantaapp.Calciatore'),
        ),
        migrations.AddField(
            model_name='ruolo',
            name='redazione',
            field=models.ForeignKey(to='fantaapp.Redazione'),
        ),
    ]
