# Generated by Django 2.2.13 on 2020-07-10 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0011_auto_20200710_0133'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_picture',
            field=models.ImageField(default='user/profile_pictures/default_profile_picture.jpg', upload_to='user/profile_pictures'),
        ),
    ]