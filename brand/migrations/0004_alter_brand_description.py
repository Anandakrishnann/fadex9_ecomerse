# Generated by Django 5.0.6 on 2024-07-02 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brand', '0003_alter_brand_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brand',
            name='description',
            field=models.TextField(default=True, max_length=500),
        ),
    ]
