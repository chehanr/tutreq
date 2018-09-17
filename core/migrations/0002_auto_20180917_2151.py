# Generated by Django 2.0.7 on 2018-09-17 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='archive_unarchive_date_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='request',
            name='archived',
            field=models.BooleanField(default=False),
        ),
    ]