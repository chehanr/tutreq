from django.core.validators import (MaxValueValidator, RegexValidator,
                                    ValidationError)
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .constants import (AVAILABLE_TIMES, DAYS_OF_WEEK, PHONE_REGEX,
                        STUDENT_ID_REGEX)

# Create your models here.


class UpperCaseCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        super(UpperCaseCharField, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname, None)
        if value:
            value = value.upper()
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super(UpperCaseCharField, self).pre_save(model_instance, add)


class Program(models.Model):
    title = models.CharField(max_length=80)

    def __str__(self):
        return self.title


class Course(models.Model):
    title = models.CharField(max_length=80)
    program = models.ForeignKey(
        Program, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.title


class Unit(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, blank=True, null=True)
    code = UpperCaseCharField(max_length=10)
    title = models.CharField(max_length=30)

    def __str__(self):
        return '{0} ({1})'.format(self.code, self.title)


class Slot(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    max_requests = models.IntegerField(
        default=1, blank=True, null=True, validators=[MaxValueValidator(5)])
    day = models.CharField(max_length=1, choices=DAYS_OF_WEEK)
    time = models.CharField(max_length=1, choices=AVAILABLE_TIMES)
    disabled = models.BooleanField(default=False)

    def __str__(self):
        day_val = [day[1]
                   for day in DAYS_OF_WEEK if day[0] == self.day][0]
        time_val = [time[1]
                    for time in AVAILABLE_TIMES if time[0] == self.time][0]

        return '{0} ({1}: {2})'.format(self.unit.code,
                                       day_val,
                                       time_val)


class Request(models.Model):
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE)
    student_id_regex = RegexValidator(
        regex=STUDENT_ID_REGEX,
        message='Student ID must be entered in the format: \'KABCD171\'.')
    student_id = UpperCaseCharField(
        validators=[student_id_regex], max_length=10)
    student_name = models.CharField(max_length=70)
    description = models.CharField(max_length=200, blank=True, null=True)
    phone_regex = RegexValidator(
        regex=PHONE_REGEX,
        message='Phone number must be entered in a correct format. Eg: \'+99 999 9999\'.')
    student_phone_number = models.CharField(
        validators=[phone_regex], max_length=17)
    date_time = models.DateTimeField(auto_now_add=True, blank=True)
    dismiss_relodge_date_time = models.DateTimeField(blank=True, null=True)
    dismissed = models.BooleanField(default=False)

    def dismiss_relodge(self):
        """ Dismiss or relodge a request. """

        self.dismiss_relodge_date_time = timezone.now()
        if self.dismissed:
            self.dismissed = False
        else:
            self.dismissed = True

        self.save()

    def __str__(self):
        return '{0}: {1}'.format(self.slot, self.student_id)
