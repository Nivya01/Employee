# Generated by Django 5.1.5 on 2025-01-27 11:32

import crud.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crud', '0007_alter_employeechildren_child_age'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeechildren',
            name='child_age',
            field=models.IntegerField(validators=[crud.models.validate_child_age]),
        ),
    ]
