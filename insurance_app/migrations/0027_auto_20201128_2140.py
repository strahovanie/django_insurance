# Generated by Django 3.1.2 on 2020-11-28 19:40

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insurance_app', '0026_auto_20201114_2026'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyuser',
            name='contract',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 11, 28, 21, 40, 58, 726801)),
        ),
        migrations.AlterField(
            model_name='request',
            name='request_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 11, 28, 21, 40, 58, 725804)),
        ),
    ]
