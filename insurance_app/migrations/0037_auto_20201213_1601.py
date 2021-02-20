# Generated by Django 3.1.2 on 2020-12-13 14:01

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insurance_app', '0036_auto_20201212_1908'),
    ]

    operations = [
        migrations.AddField(
            model_name='documents',
            name='received',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='documents',
            name='sended',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 12, 13, 16, 1, 3, 205606)),
        ),
        migrations.AlterField(
            model_name='request',
            name='request_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 12, 13, 16, 1, 3, 205606)),
        ),
    ]