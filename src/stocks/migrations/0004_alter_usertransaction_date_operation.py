# Generated by Django 4.2.5 on 2023-09-17 22:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0003_alter_usertransaction_date_operation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertransaction',
            name='date_operation',
            field=models.DateField(default=datetime.datetime(2023, 9, 18, 8, 35, 16, 202709)),
        ),
    ]
