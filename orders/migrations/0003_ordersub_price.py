# Generated by Django 5.0.6 on 2024-07-29 05:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_alter_ordermain_order_id_alter_ordermain_payment_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordersub',
            name='price',
            field=models.FloatField(default=0),
        ),
    ]
