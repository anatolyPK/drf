# Generated by Django 4.2.5 on 2023-09-18 04:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crypto', '0022_alter_personstransactions_date_operation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personstransactions',
            name='date_operation',
            field=models.DateField(default=datetime.datetime(2023, 9, 18, 4, 53, 47, 45025, tzinfo=datetime.timezone.utc)),
        ),
    ]
