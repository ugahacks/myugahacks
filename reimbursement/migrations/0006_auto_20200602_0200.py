# Generated by Django 2.2.10 on 2020-06-02 07:00

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
