# Generated by Django 5.2.1 on 2025-07-18 07:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exporters_app', '0004_otp'),
    ]

    operations = [
        migrations.AddField(
            model_name='otp',
            name='purpose',
            field=models.CharField(choices=[('reset', 'Password Reset'), ('2fa', 'Two-Factor Authentication')], default='reset', max_length=10),
        ),
    ]
