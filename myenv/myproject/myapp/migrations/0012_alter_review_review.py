# Generated by Django 5.1.6 on 2025-03-20 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0011_remove_review_rdate_remove_review_text_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='review',
            field=models.TextField(blank=True, default='No Review'),
        ),
    ]
