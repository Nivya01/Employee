# Generated by Django 5.1.5 on 2025-01-22 08:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crud', '0002_employee_email_alter_employee_emp_age_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
