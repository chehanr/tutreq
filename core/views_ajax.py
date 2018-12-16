from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse

from .models import Request, Slot
from .utils import (get_day_val, get_next_date_time, get_request_item_dict,
                    get_time_val)

# Ajax responses:


@staff_member_required
def dismiss_relodge_request(request):
    """Json response to get request information and set dismiss/ relodge info."""

    request_id = request.GET.get('request-id')
    status_code = 200

    try:
        request_obj = Request.objects.get(pk=request_id)
        request_obj.dismiss_relodge()

        response_dict = {
            'id': request_obj.pk,
            'text': str(request_obj),
            'dismissed': request_obj.dismissed,
            'dismiss_relodge_date_time': request_obj.dismiss_relodge_date_time,
        }

    except ObjectDoesNotExist as err:
        status_code = 400
        response_dict = {
            'request': None,
            'error': str(err),
        }

    return JsonResponse(response_dict, status=status_code)


@staff_member_required
def archive_unarchive_request(request):
    """Json response to get request information and set archive/ unarchive info."""

    request_id = request.GET.get('request-id')
    status_code = 200

    try:
        request_obj = Request.objects.get(pk=request_id)
        request_obj.archive_unarchive()

        response_dict = {
            'id': request_obj.pk,
            'text': str(request_obj),
            'archived': request_obj.archived,
            'archive_unarchive_date_time': request_obj.archive_unarchive_date_time,
        }

    except ObjectDoesNotExist as err:
        status_code = 400
        response_dict = {
            'request': None,
            'error': str(err),
        }

    return JsonResponse(response_dict, status=status_code)


@staff_member_required
def request_info(request):
    """Json response to get request information."""

    request_id = request.GET.get('request-id')
    status_code = 200

    try:
        request_obj = Request.objects.get(pk=request_id)
        request_item = get_request_item_dict(request_obj)

        response_dict = {
            'request': request_item,
        }
    except ObjectDoesNotExist as err:
        status_code = 400
        response_dict = {
            'request': None,
            'error': str(err),
        }

    return JsonResponse(response_dict, status=status_code)


def slots_info(request):
    """Json response to get slot information."""

    unit_id = request.GET.get('unit-id')
    status_code = 200

    slot_objs = Slot.objects.filter(unit=unit_id, disabled=False)
    slot_items = []

    for slot_obj in slot_objs:
        slot = slot_obj
        slot_day = slot.day
        slot_time = slot.time
        slot_disabled = slot.disabled

        unit = slot.unit
        unit_code = unit.code
        unit_course = unit.course.title
        unit_title = unit.title

        slot_item = {
            'id': slot.pk,
            'text': str(slot),
            'day': get_day_val(slot_day),
            'time': get_time_val(slot_time),
            'next_date_time': get_next_date_time(slot_day),
            'disabled': slot_disabled,
            'unit': {
                'code': unit_code,
                'course': unit_course,
                'title': unit_title,
            },
        }

        slot_items.append(slot_item)

    if slot_items:
        response_dict = {
            'slots': slot_items,
        }
    else:
        status_code = 400
        response_dict = {
            'slots': None,
        }

    return JsonResponse(response_dict, status=status_code)


def request_count(request):
    """Json response to get request count."""

    status_code = 200

    request_obj_count = Request.objects.count()

    if request_obj_count:
        response_dict = {
            'request_count': request_obj_count,
        }
    else:
        status_code = 400
        response_dict = {
            'request_count': None,
        }

    return JsonResponse(response_dict, status=status_code)
