# Generated by Django 4.2.5 on 2023-09-18 00:42

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crypto', '0014_alter_personstransactions_date_operation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personstransactions',
            name='date_operation',
            field=models.DateField(default=datetime.datetime(2023, 9, 18, 0, 42, 20, 671589, tzinfo=datetime.timezone.utc)),
        ),
    ]
