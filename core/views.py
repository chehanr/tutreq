from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import get_template

from easy_pdf.rendering import render_to_pdf_response

from .forms import RequestForm
from .models import Request, Slot, Unit
from .utils import get_day_val, get_next_date_time, get_time_val

# Create your views here.

# Non-view methods:


def get_request_item_dict(request_id):
    request_obj = Request.objects.get(pk=request_id)

    slot = request_obj.slot
    slot_day = slot.day
    slot_time = slot.time
    slot_disabled = slot.disabled

    unit = slot.unit
    unit_code = unit.code
    unit_title = unit.title
    unit_course = unit.course.title
    unit_program = unit.course.program.title

    request_item = {
        'id': request_obj.pk,
        'text': str(request_obj),
        'date_time': request_obj.date_time,
        'dismissed': request_obj.dismissed,
        'dismiss_relodge_date_time': request_obj.dismiss_relodge_date_time,
        'description': request_obj.description,
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
    }

    return request_item


@staff_member_required
def requests_manage(request):
    request_objs = Request.objects.all().order_by('dismissed', '-date_time')
    page = request.GET.get('page', 1)
    paginator = Paginator(request_objs, 10)

    try:
        requests = paginator.page(page)
    except PageNotAnInteger:
        requests = paginator.page(1)
    except EmptyPage:
        requests = paginator.page(paginator.num_pages)

    return render(request, 'requests_manage.html', {'requests': requests,
                                                    'nbar_active': 'requests_manage', })


def request_form(request):
    unit_objs = Unit.objects.all().order_by('course')

    # TODO Find a cleaner way.
    course_items = {'courses': []}

    for unit_obj in unit_objs:
        course_title = unit_obj.course.title

        course_item = {
            'title': course_title,
            'units': [],
        }

        course_items['courses'].append(course_item)

    course_items['courses'] = list(
        {item['title']: item for item in course_items['courses']}.values())

    for unit_obj in unit_objs:
        unit_id = unit_obj.pk
        unit_title = unit_obj.title
        unit_code = unit_obj.code
        course_title = unit_obj.course.title
        has_slots = False

        if Slot.objects.filter(unit=unit_id):
            has_slots = True

        unit_item = {
            'id': unit_id,
            'title': unit_title,
            'code': unit_code,
            'has_slots': has_slots,
        }

        for course_item in course_items['courses']:
            if course_item['title'] == course_title:
                course_item['units'].append(unit_item)

    if request.method == 'POST':
        form = RequestForm(request.POST)

        if form.is_valid():
            request_obj = form.save()
            submission_text = ('Your tutor request (id: {0}) has been '
                               'submitted and will be reviewed shortly.').format(request_obj.pk)
            # Reset the form.
            form = RequestForm()

            messages.success(request, 'Request submission successful!',
                             extra_tags=submission_text)

    else:
        form = RequestForm()

    return render(request, 'request_form.html', {'form': form,
                                                 'select_items': course_items,
                                                 'nbar_active': 'request_form', })


@staff_member_required
def generate_pdf(request):
    # TODO show generated time.
    request_id = request.GET.get('request-id')
    request_item = get_request_item_dict(request_id)

    template = 'pdf_template.html'
    context = {'request': request_item}

    pdf_filename = 'tutreq_request_{0}.pdf'.format(request_item['id'])

    return render_to_pdf_response(request, template, context, filename=pdf_filename)
    # return render(request, 'pdf_template.html', {'request': request_item,})

# Ajax responses:


@staff_member_required
def dismiss_relodge_request(request):
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
def request_info_json(request):
    request_id = request.GET.get('request-id')
    status_code = 200

    try:
        request_item = get_request_item_dict(request_id)

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


def slots_info_json(request):
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
