# Generated by Django 5.0.6 on 2024-07-18 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_panel', '0002_alter_useraddress_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraddress',
            name='order_status',
            field=models.BooleanField(default=False),
        ),
    ]