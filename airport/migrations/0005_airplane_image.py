# Generated by Django 4.2.11 on 2024-05-15 09:48

import airport.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airport', '0004_alter_ticket_options_remove_ticket_unique_seat_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='airplane',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=airport.models.create_custom_path),
        ),
    ]
