# Generated by Django 3.0.8 on 2020-07-26 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pdl', '0007_proyecto_titulo2'),
    ]

    operations = [
        migrations.AddField(
            model_name='proyecto',
            name='seguimiento',
            field=models.TextField(blank=True),
        ),
    ]
