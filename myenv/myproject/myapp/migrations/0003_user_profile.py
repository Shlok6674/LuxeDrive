# Generated by Django 5.1.6 on 2025-03-05 09:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_rename_password_user_password1'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profile',
            field=models.ImageField(default='', upload_to=''),
        ),
    ]
