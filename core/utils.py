from datetime import timedelta

from django.utils import timezone

from .constants import AVAILABLE_TIMES, DAYS_OF_WEEK, SATISFACTION_LEVELS


def get_next_date_time(day):
    """
     Returns the next possible slot's `date_time`
     TODO: calculate with time slots.

    """

    day = int(day)
    today = timezone.now()

    if day > today.weekday():
        date_time = today + timedelta(days=day - today.weekday())
    elif day == today.weekday():
        date_time = today + timedelta(days=7)
    else:
        date_time = today + timedelta(days=7 - today.weekday() + day)

    return date_time.replace(minute=0, hour=0, second=0, microsecond=0)


def get_day_val(day_key):
    day_val = [day[1]
               for day in DAYS_OF_WEEK if day[0] == day_key][0]

    return day_val


def get_time_val(time_key):
    time_val = [time[1]
                for time in AVAILABLE_TIMES if time[0] == time_key][0]

    return time_val


def get_satisfaction_val(satis_key):
    satis_val = [satis[1]
                 for satis in SATISFACTION_LEVELS if satis[0] == satis_key][0]

    return satis_val
