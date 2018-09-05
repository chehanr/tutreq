import csv

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from easy_pdf.rendering import render_to_pdf_response

from .forms import FeedbackForm, RequestFeedbackRefField, RequestForm
from .models import Feedback, Request, Slot, Unit
from .utils import (get_day_val, get_next_date_time, get_satisfaction_val,
                    get_time_val)

# Create your views here.

# Non-view methods:


def get_request_item_dict(request_obj):
    """Method to format request objects and return a dictionary."""

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


@staff_member_required
def requests_manage(request):
    """View for `requests_manage`."""

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


def request_feedback(request, ref=None):
    """View for `request_feedback`."""

    if ref:
        ref = ref.upper()
        request_obj = get_object_or_404(Request, feedback_ref=ref)
        try:
            feedback_obj = Feedback.objects.get(request=request_obj)
            locked = feedback_obj.locked
        except ObjectDoesNotExist:
            locked = False

        if locked is False:
            if request.method == 'POST':
                form = FeedbackForm(request.POST)

                if form.is_valid():
                    feedback_obj = form.save(commit=False)
                    feedback_obj.request = request_obj
                    feedback_obj.locked = True
                    feedback_obj.save()
                    submission_text = ('Your feedback for request id: {0} has been '
                                       'submitted!').format(request_obj.pk)

                    messages.success(request, 'Feedback submission successful!',
                                     extra_tags=submission_text)

            else:
                form = FeedbackForm()

            return render(request, 'request_feedback.html', {'form': form,
                                                             'form_method': 'post',
                                                             'form_submit_button': 'Submit feedback',
                                                             'nbar_active': 'request_feedback', })
        else:
            # TODO show locked msg.
            return redirect('request_feedback')

    else:
        if request.method == 'GET':
            form = RequestFeedbackRefField(request.GET)

            if form.is_valid():
                feedback_ref = form.cleaned_data.get('reference_code')
                return redirect('request_feedback', ref=feedback_ref)

        else:
            form = RequestFeedbackRefField()

        return render(request, 'request_feedback.html', {'form': form,
                                                         'form_method': 'get',
                                                         'form_submit_button': 'Find',
                                                         'nbar_active': 'request_feedback', })


def request_form(request):
    """View for `request_form`."""

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
                               'submitted and will be reviewed shortly. '
                               'Feedback reference code: {1}').format(request_obj.pk,
                                                                      request_obj.feedback_ref)
            # Reset the form.
            form = RequestForm()

            messages.success(request, 'Request submission successful!',
                             extra_tags=submission_text)

    else:
        form = RequestForm()

    return render(request, 'request_form.html', {'form': form,
                                                 'select_items': course_items,
                                                 'nbar_active': 'request_form', })


def about_page(request):
    """Displays a static about page."""

    return render(request, 'about_page.html', {'nbar_active': 'about_page', })


@staff_member_required
def generate_pdf(request):
    """Generates a pdf file specific request object."""

    request_id = request.GET.get('request-id')
    request_obj = Request.objects.get(pk=request_id)
    request_item = get_request_item_dict(request_obj)
    gen_date_time = timezone.now()

    template = 'pdf_template.html'
    context = {'request': request_item, 'generated_date_time': gen_date_time}
    pdf_filename = 'tutreq_request_{0}.pdf'.format(request_item['id'])

    return render_to_pdf_response(request, template, context, filename=pdf_filename)


class Buffer:
    """An object that implements just the write method of the file-like
    interface.

    C & V from: https://docs.djangoproject.com/en/2.1/howto/outputting-csv/#streaming-large-csv-files
    """

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


@staff_member_required
def generate_csv(request, rid=None):
    """Generates a csv file with all (or specific `rid`) request object(s)."""

    request_items_dict = get_request_items_dict(rid)
    rows = []

    row_header = (
        'Request ID', 'Request identifier', 'Request made on',
        'Student ID', 'Student name', 'Student phone number',
        'Request dismissed status', 'Request dismissed/ relodged time', 'Request notes',
        'Request feedback code', 'Slot', 'Slot day', 
        'Slot time', 'Slot disabled status', 'Unit code', 
        'Unit title', 'Unit program', 'Feeback satisfaction', 
        'Feedback comment', 'Feedback made on'
    )

    rows.append(row_header)

    for request_item in request_items_dict['request_items']:
        row = [
            request_item['id'], request_item['text'], request_item['date_time'],
            request_item['student']['id'], request_item['student']['name'], request_item['student']['phone'], 
            request_item['dismissed'], request_item['dismiss_relodge_date_time'], request_item['description'], 
            request_item['feedback_ref_code'], request_item['slot']['text'], request_item['slot']['day'], 
            request_item['slot']['time'], request_item['slot']['disabled'], request_item['unit']['code'], 
            request_item['unit']['title'], request_item['unit']['program'],
        ]

        if request_item['feedback']:
            feedback_item = [
                request_item['feedback']['satisfaction_val'],
                request_item['feedback']['description'],
                request_item['feedback']['date_time'],
            ]

            row.extend(feedback_item)

        rows.append(tuple(row))

    pseudo_buffer = Buffer()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                     content_type="text/csv")

    csv_filename = 'tutreq_log.csv'
    if rid:
        csv_filename = 'tutreq_log_r-{}.csv'.format(rid)

    response['Content-Disposition'] = 'attachment; filename="{}"'.format(
        csv_filename)

    return response

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
def request_info_json(request):
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


def slots_info_json(request):
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
