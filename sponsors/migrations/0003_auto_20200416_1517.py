# Generated by Django 2.2.10 on 2020-04-16 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sponsors', '0002_auto_20200320_1654'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sponsor',
            name='company',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='sponsor',
            name='email_domain',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
