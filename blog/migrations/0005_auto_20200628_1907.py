# Generated by Django 2.2.13 on 2020-06-28 23:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_auto_20200531_0117'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='blog',
            name='content',
            field=models.CharField(max_length=16384),
        ),
    ]
