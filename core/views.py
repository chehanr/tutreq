from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FeedbackForm, RequestFeedbackRefField, RequestForm
from .models import Feedback, Request, Slot, Unit

# Create your views here.


@staff_member_required
def manage(request, view_type=None):
    """View for `manage`."""

    if view_type == 'all':
        request_objs = Request.objects.all().order_by('-date_time')
    elif view_type == 'archive':
        request_objs = Request.objects.filter(
            archived=True).order_by('-date_time')
    elif view_type == '!archive':
        request_objs = Request.objects.filter(
            archived=False).order_by('-date_time')
    elif view_type == 'dismissed':
        request_objs = Request.objects.filter(
            dismissed=True).order_by('-date_time')
    elif view_type == '!dismissed':
        request_objs = Request.objects.filter(
            dismissed=False).order_by('-date_time')
    else:
        request_objs = Request.objects.filter(
            archived=False).order_by('dismissed', '-date_time')

    page = request.GET.get('page', 1)
    paginator = Paginator(request_objs, 10)

    try:
        requests = paginator.page(page)
    except PageNotAnInteger:
        requests = paginator.page(1)
    except EmptyPage:
        requests = paginator.page(paginator.num_pages)

    return render(request, 'manage.html', {'requests': requests,
                                           'nbar_active': 'manage', })


def feedback(request, ref=None):
    """View for `feedback`."""

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

                    message_title = 'Feedback submission successful!'
                    message_text = ('Your feedback for reference code: {0} has been '
                                    'submitted!').format(request_obj.feedback_ref)

                    messages.success(request, message_title,
                                     extra_tags=message_text)

            else:
                form = FeedbackForm()

            return render(request, 'feedback.html', {'form': form,
                                                     'form_method': 'post',
                                                     'form_submit_button': 'Submit feedback',
                                                     'nbar_active': 'feedback', })
        else:
            # TODO show locked msg.
            return redirect('feedback')

    else:
        if request.method == 'GET':
            form = RequestFeedbackRefField(request.GET)

            if form.is_valid():
                feedback_ref = form.cleaned_data.get('reference_code')
                return redirect('feedback', ref=feedback_ref)

        else:
            form = RequestFeedbackRefField()

        return render(request, 'feedback.html', {'form': form,
                                                 'form_method': 'get',
                                                 'form_submit_button': 'Find',
                                                 'nbar_active': 'feedback', })


def home(request):
    """View for `home`."""

    unit_objs = Unit.objects.all().order_by('course')

    course_items = {'courses': []}

    for unit_obj in unit_objs:
        unit_id = unit_obj.pk
        unit_title = unit_obj.title
        unit_code = unit_obj.code
        course_title = unit_obj.course.title
        has_slots = False

        if Slot.objects.filter(unit=unit_id):
            has_slots = True

        course_item = {
            'title': course_title,
            'units': [],
        }

        unit_item = {
            'id': unit_id,
            'title': unit_title,
            'code': unit_code,
            'has_slots': has_slots,
        }

        course_items['courses'].append(course_item)

        for course_item in course_items['courses']:
            if course_item['title'] == course_title:
                course_item['units'].append(unit_item)

    if request.method == 'POST':
        form = RequestForm(request.POST)

        if form.is_valid():
            request_obj = form.save()
            message_title = 'Your session is confirmed! Make sure to attend the tutoring session on time.'
            message_text = ('Your tutor request has been '
                            'submitted and will be reviewed shortly.<br/>'
                            'Feedback reference code: <strong>{0}</strong><br/>').format(request_obj.feedback_ref)
            # Reset the form.
            form = RequestForm()

            messages.success(request, message_title, extra_tags=message_text)

    else:
        form = RequestForm()

    return render(request, 'home.html', {'form': form,
                                         'select_items': course_items,
                                         'nbar_active': 'home', })


def about(request):
    """Displays a static about page."""

    return render(request, 'about.html', {'nbar_active': 'about', })
