# Generated by Django 5.0.6 on 2024-06-25 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0002_accounts_groups_accounts_is_superuser_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='accounts',
            name='is_staff',
            field=models.BooleanField(default=False),
        ),
    ]
