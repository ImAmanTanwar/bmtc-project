# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BusStops',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stop_name', models.CharField(max_length=200)),
                ('latitude', models.CharField(max_length=25)),
                ('longitude', models.CharField(max_length=25)),
            ],
        ),
    ]
