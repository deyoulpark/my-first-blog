# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-20 07:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_uploadfilemodel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadfilemodel',
            name='title',
            field=models.CharField(max_length=50),
        ),
    ]