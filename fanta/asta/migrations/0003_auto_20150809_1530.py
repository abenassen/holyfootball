# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantaapp', '0023_auto_20150809_1530'),
        ('asta', '0002_auto_20150804_1309'),
    ]

    operations = [
        migrations.CreateModel(
            name='Asta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creata', models.DateTimeField(editable=False)),
                ('modificata', models.DateTimeField()),
                ('iniziale', models.BooleanField(default=True)),
                ('lega', models.ForeignKey(to='fantaapp.Lega')),
            ],
        ),
        migrations.AddField(
            model_name='calciatorechiamato',
            name='asta',
            field=models.ForeignKey(default=0, to='asta.Asta'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='offerta',
            name='asta',
            field=models.ForeignKey(default=0, to='asta.Asta'),
            preserve_default=False,
        ),
    ]
