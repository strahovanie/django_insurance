# Generated by Django 3.1.2 on 2020-11-29 17:33

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insurance_app', '0031_auto_20201129_1918'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='contract',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 11, 29, 19, 33, 6, 409850)),
        ),
        migrations.AlterField(
            model_name='request',
            name='request_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 11, 29, 19, 33, 6, 409850)),
        ),
    ]