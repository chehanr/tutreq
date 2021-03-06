# Generated by Django 2.0.7 on 2018-08-04 10:22

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models

import core.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=80)),
            ],
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('satisfaction', models.CharField(choices=[('0', 'Very satisfied'), ('1', 'Satisfied'), ('2', 'OK'), ('3', 'Dissatisfied'), ('4', 'Very dissatisfied')], max_length=1)),
                ('description', models.CharField(blank=True, max_length=200, null=True)),
                ('date_time', models.DateTimeField(auto_now_add=True)),
                ('locked', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=80)),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_id', core.models.UpperCaseCharField(max_length=10, validators=[django.core.validators.RegexValidator(message="Student ID must be entered in the format: 'KABCD171'.", regex='^[A-Za-z]{5}\\d{3}$')])),
                ('student_name', models.CharField(max_length=70)),
                ('description', models.CharField(blank=True, max_length=200, null=True)),
                ('student_phone_number', models.CharField(max_length=17, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in a correct format. Eg: '+99 999 9999'.", regex='^\\s*(?:\\+?(\\d{1,3}))?[-. (]*(\\d{3})[-. )]*(\\d{3})[-. ]*(\\d{4})(?: *x(\\d+))?\\s*$')])),
                ('date_time', models.DateTimeField(auto_now_add=True)),
                ('dismiss_relodge_date_time', models.DateTimeField(blank=True, null=True)),
                ('dismissed', models.BooleanField(default=False)),
                ('feedback_ref', models.CharField(blank=True, default=core.models.ref_code_gen, max_length=10, null=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Slot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('max_requests', models.IntegerField(blank=True, default=1, null=True, validators=[django.core.validators.MaxValueValidator(5)])),
                ('day', models.CharField(choices=[('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'), ('3', 'Thursday'), ('4', 'Friday'), ('5', 'Saturday'), ('6', 'Sunday')], max_length=1)),
                ('time', models.CharField(choices=[('0', '9:00 - 11:00'), ('1', '12:00 - 14:00'), ('2', '14:00 - 16:00')], max_length=1)),
                ('disabled', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', core.models.UpperCaseCharField(max_length=10)),
                ('title', models.CharField(max_length=100)),
                ('course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Course')),
            ],
        ),
        migrations.AddField(
            model_name='slot',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Unit'),
        ),
        migrations.AddField(
            model_name='request',
            name='slot',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Slot'),
        ),
        migrations.AddField(
            model_name='feedback',
            name='request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Request'),
        ),
        migrations.AddField(
            model_name='course',
            name='program',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Program'),
        ),
    ]
