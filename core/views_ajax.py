from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.db.models import Q

from .models import Request, Slot
from .utils import  get_next_date_time, get_request_item_dict

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

def slots_search(request):
    """ Json response to search slots. """

    status_code = 200
    response_dict = {
        'status': False,
    }

    if request.is_ajax() and request.method == 'GET':
        search_q = request.GET.get('q', None)

        if search_q:
            search_q = search_q.strip()
            slot_objs = Slot.objects.filter(Q(unit__title__icontains=search_q) | Q(unit__code__icontains=search_q))

        if slot_objs:
            result_list = []

            for slot_obj in slot_objs:
                result_item = {
                    'id': slot_obj.pk,
                    'text': str(slot_obj),
                    'day': slot_obj.get_day_display(),
                    'time': slot_obj.get_time_display(),
                    'next_date_time': get_next_date_time(slot_obj.day),
                    'disabled': slot_obj.disabled,
                    'unit': {
                        'code': slot_obj.unit.code,
                        'course': slot_obj.unit.course.title,
                        'program': slot_obj.unit.course.program.title,
                        'title': slot_obj.unit.title,
                    },
                }

                result_list.append(result_item)

            response_dict['status'] = True
            response_dict['results'] = result_list
        else:
            response_dict['results'] = []

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
