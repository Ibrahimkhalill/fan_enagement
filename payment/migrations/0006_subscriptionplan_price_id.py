# Generated by Django 5.1.6 on 2025-04-24 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0005_alter_description_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriptionplan',
            name='price_id',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
