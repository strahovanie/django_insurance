# Generated by Django 3.1.2 on 2020-11-29 16:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insurance_app', '0028_auto_20201128_2220'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='user_company',
        ),
        migrations.AlterField(
            model_name='order',
            name='order_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 11, 29, 18, 13, 8, 859776)),
        ),
        migrations.AlterField(
            model_name='request',
            name='request_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 11, 29, 18, 13, 8, 858773)),
        ),
    ]
