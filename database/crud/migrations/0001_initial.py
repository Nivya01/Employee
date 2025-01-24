# Generated by Django 5.1.5 on 2025-01-17 08:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('emp_id', models.AutoField(primary_key=True, serialize=False)),
                ('emp_name', models.CharField(max_length=100)),
                ('emp_age', models.IntegerField()),
                ('emp_gender', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='EmployeeChildren',
            fields=[
                ('child_id', models.AutoField(primary_key=True, serialize=False)),
                ('child_name', models.CharField(max_length=100)),
                ('child_age', models.IntegerField()),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='children', to='crud.employee')),
            ],
        ),
    ]
