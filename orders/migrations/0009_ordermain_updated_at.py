# Generated by Django 5.0.6 on 2024-08-07 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_ordermain_discount_amount_ordermain_final_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordermain',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
