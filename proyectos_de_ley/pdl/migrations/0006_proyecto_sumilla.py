# Generated by Django 3.0.8 on 2020-07-26 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pdl', '0005_proyecto_legislatura_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='proyecto',
            name='sumilla',
            field=models.TextField(null=True),
        ),
    ]
