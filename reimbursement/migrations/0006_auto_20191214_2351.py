# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-12-15 04:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reimbursement', '0005_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reimbursement',
            name='assigned_money',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
