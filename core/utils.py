from .constants import AVAILABLE_TIMES, DAYS_OF_WEEK, SATISFACTION_LEVELS


def get_next_date_time(day):
    """
     Returns the next possible slot's `date_time`
     TODO: calculate with time slots.

    """

    from datetime import timedelta
    from django.utils import timezone

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


def get_request_item_dict(request_obj):
    """Method to format request objects and return a dictionary."""

    from django.core.exceptions import ObjectDoesNotExist
    from .models import Feedback

    slot = request_obj.slot
    slot_day = slot.day
    slot_time = slot.time
    slot_disabled = slot.disabled

    unit = slot.unit
    unit_code = unit.code
    unit_title = unit.title
    unit_course = unit.course.title
    unit_program = unit.course.program.title

    try:
        feedback_obj = Feedback.objects.get(request=request_obj)
    except ObjectDoesNotExist:
        feedback_dict = None
    else:
        feedback = feedback_obj
        feedback_satisfaction_level = feedback.satisfaction
        feedback_satisfaction_val = get_satisfaction_val(feedback.satisfaction)
        feedback_description = feedback.description
        feedback_date_time = feedback.date_time
        feedback_dict = {
            'id': feedback.pk,
            'text': str(feedback),
            'satisfaction': feedback_satisfaction_level,
            'satisfaction_val': feedback_satisfaction_val,
            'description': feedback_description,
            'date_time': feedback_date_time,
        }

    request_item = {
        'id': request_obj.pk,
        'text': str(request_obj),
        'date_time': request_obj.date_time,
        'dismissed': request_obj.dismissed,
        'dismiss_relodge_date_time': request_obj.dismiss_relodge_date_time,
        'archived': request_obj.archived,
        'archive_unarchive_date_time': request_obj.archive_unarchive_date_time,
        'description': request_obj.description,
        'feedback_ref_code': request_obj.feedback_ref,
        'slot': {
            'id': slot.pk,
            'text': str(slot),
            'day': get_day_val(slot_day),
            'time': get_time_val(slot_time),
            'next_date_time': get_next_date_time(slot_day),
            'disabled': slot_disabled,
        },
        'unit': {
            'text': str(unit),
            'code': unit_code,
            'title': unit_title,
            'course': unit_course,
            'program': unit_program,
        },
        'student': {
            'id': request_obj.student_id,
            'name': request_obj.student_name,
            'phone': request_obj.student_phone_number,
        },
        'feedback': feedback_dict,
    }

    return request_item


def get_request_items_dict(request_id=None):
    """Method to iterate through request objects and return a dictionary."""

    from django.shortcuts import get_object_or_404
    from .models import Request

    request_items = {'request_items': []}

    if request_id:
        request_obj = get_object_or_404(Request, pk=request_id)
        request_item = get_request_item_dict(request_obj)
        request_items['request_items'].append(request_item)
    else:
        for request_obj in Request.objects.all():
            request_item = get_request_item_dict(request_obj)
            request_items['request_items'].append(request_item)

    return request_items
