# Generated by Django 5.1.4 on 2025-01-06 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_remove_product_description_alter_product_price'),
        ('record', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='products',
            field=models.ManyToManyField(related_name='products', to='product.product'),
        ),
    ]
