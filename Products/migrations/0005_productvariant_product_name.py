# Generated by Django 5.0.6 on 2024-07-01 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_alter_products_product_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='productvariant',
            name='product_name',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
    ]