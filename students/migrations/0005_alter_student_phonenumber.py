# Generated by Django 4.2.10 on 2025-03-06 07:36

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("students", "0004_student_is_active"),
    ]

    operations = [
        migrations.AlterField(
            model_name="student",
            name="phoneNumber",
            field=models.CharField(
                max_length=15,
                validators=[
                    django.core.validators.RegexValidator(
                        message="Enter a valid phone number.", regex="^\\d{10,15}$"
                    )
                ],
            ),
        ),
    ]
