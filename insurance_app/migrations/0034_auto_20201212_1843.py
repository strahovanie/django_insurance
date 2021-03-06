# Generated by Django 3.1.2 on 2020-12-12 16:43

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insurance_app', '0033_auto_20201212_1840'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documents',
            name='current_payment_amount',
            field=models.FloatField(blank=True),
        ),
        migrations.AlterField(
            model_name='documents',
            name='file_location',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='documents',
            name='full_payment_amount',
            field=models.FloatField(blank=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 12, 12, 18, 43, 25, 565533)),
        ),
        migrations.AlterField(
            model_name='request',
            name='request_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 12, 12, 18, 43, 25, 565533)),
        ),
    ]
