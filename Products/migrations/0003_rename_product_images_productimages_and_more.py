# Generated by Django 5.0.6 on 2024-06-28 12:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_alter_product_images_images'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Product_Images',
            new_name='ProductImages',
        ),
        migrations.RenameModel(
            old_name='Product_Variant',
            new_name='ProductVariant',
        ),
    ]
