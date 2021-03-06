# Generated by Django 3.1.2 on 2020-11-28 20:20

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('insurance_app', '0027_auto_20201128_2140'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='companyuser',
            name='contract',
        ),
        migrations.AlterField(
            model_name='order',
            name='order_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 11, 28, 22, 20, 1, 278647)),
        ),
        migrations.AlterField(
            model_name='request',
            name='request_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 11, 28, 22, 20, 1, 277649)),
        ),
        migrations.CreateModel(
            name='CompanyUserContract',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contract', models.BooleanField(default=False)),
                ('company_info', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='insurance_app.companyinfo')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
