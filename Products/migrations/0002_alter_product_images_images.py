# Generated by Django 5.0.6 on 2024-06-27 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product_images',
            name='images',
            field=models.ImageField(default='C:\\FADEX.9\\FADEX9\\static\\product_images\no image.webp', upload_to='product_images'),
        ),
    ]
