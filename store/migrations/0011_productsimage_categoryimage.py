# Generated by Django 4.2.1 on 2023-06-16 17:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_order_order_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductsImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='store/image')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='image', to='store.products')),
            ],
        ),
        migrations.CreateModel(
            name='CategoryImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='store/image')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='image', to='store.category')),
            ],
        ),
    ]
