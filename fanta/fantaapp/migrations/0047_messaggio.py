# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0046_auto_20150921_2233'),
    ]

    operations = [
        migrations.CreateModel(
            name='Messaggio',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('testo', models.CharField(max_length=200)),
                ('data', models.DateField(auto_now=True)),
                ('allenatore', models.ForeignKey(blank=True, to='fantaapp.Allenatore', null=True)),
                ('lega', models.ForeignKey(to='fantaapp.Lega')),
            ],
        ),
    ]
