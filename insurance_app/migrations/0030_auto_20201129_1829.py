# Generated by Django 3.1.2 on 2020-11-29 16:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insurance_app', '0029_auto_20201129_1813'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='result_file',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 11, 29, 18, 29, 34, 97255)),
        ),
        migrations.AlterField(
            model_name='request',
            name='request_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 11, 29, 18, 29, 34, 96254)),
        ),
    ]