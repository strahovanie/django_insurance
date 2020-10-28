# Generated by Django 3.1.2 on 2020-10-28 15:04

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insurance_app', '0019_auto_20201028_1701'),
    ]

    operations = [
        migrations.RenameField(
            model_name='companyuser',
            old_name='company',
            new_name='company_info',
        ),
        migrations.RenameField(
            model_name='request',
            old_name='company',
            new_name='company_info',
        ),
        migrations.AlterField(
            model_name='request',
            name='request_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 10, 28, 17, 4, 33, 333495)),
        ),
    ]
