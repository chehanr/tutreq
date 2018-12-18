from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q

from .forms import FeedbackForm, RequestFeedbackRefField, RequestForm
from .models import Feedback, Request, Slot, Unit

# Create your views here.


@staff_member_required
def manage(request):
    """View for `manage`."""

    search_q = request.GET.get('query', None)
    searh_type_q = request.GET.get('type', None)
    filter_q = request.GET.get('filter', None)
    order_by_q = request.GET.get('order', 'pending')
    result_count_q = int(request.GET.get('count', 25))

    # Searching objects.
    if search_q:
        search_q = search_q.strip()

        if searh_type_q in ('unit', 'feedback_ref'):
            # TODO add slot search.
            if searh_type_q == 'unit':
                request_objs = Request.objects.filter(Q(slot__unit__title__icontains=search_q) | Q(slot__unit__code__icontains=search_q))
            else:
                request_objs = Request.objects.filter(feedback_ref__icontains=search_q)
        else:
            # Default to student search.
            request_objs = Request.objects.filter(Q(student_id__icontains=search_q) | Q(student_name__icontains=search_q))
    else:
        # Get all objects when no search query.
        request_objs = Request.objects.all()

    # Filtering objects.
    if filter_q in ('archived', '-archived', 'dismissed', '-dismissed'):    
        filter_q = filter_q.strip()

        if filter_q == 'archived':
            request_objs =request_objs.filter(archived=True)
        elif filter_q == '-archived':
            request_objs = request_objs.filter(archived=False)
        elif filter_q == 'dismissed':
            request_objs = request_objs.filter(dismissed=True)
        elif filter_q == '-dismissed':
            request_objs = request_objs.filter(dismissed=False)
    else:
        request_objs = request_objs.exclude(archived=True)


    # Odering objects.
    if order_by_q in ('date_time', '-date_time', 'dismissed', '-dismissed'):
        order_by_q = order_by_q.strip()
        request_objs = request_objs.order_by(order_by_q)
    else:
        # `pending` ordering.
        request_objs = request_objs.order_by('dismissed', '-date_time')

    if result_count_q not in (25, 50, 100):
        # Reset to 25 results.
        result_count_q = 25

    page = request.GET.get('page', 1)
    paginator = Paginator(request_objs, result_count_q)

    try:
        requests = paginator.page(page)
    except PageNotAnInteger:
        requests = paginator.page(1)
    except EmptyPage:
        requests = paginator.page(paginator.num_pages)

    return render(request, 'manage.html', {'requests': requests,
                                           'active_page': 'manage', })


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
                    message_text = ('Your feedback for reference code {0} has been '
                                    'submitted!').format(request_obj.feedback_ref)

                    messages.success(request, message_title,
                                     extra_tags=message_text)

            else:
                form = FeedbackForm()

            return render(request, 'feedback.html', {'form': form,
                                                     'form_method': 'POST',
                                                     'form_submit_button': 'Submit feedback',
                                                     'active_page': 'feedback', })
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
                                                 'form_method': 'GET',
                                                 'form_submit_button': 'Find',
                                                 'active_page': 'feedback', })


def home(request):
    """View for `home`."""

    if request.method == 'POST':
        form = RequestForm(request.POST)

        if form.is_valid():
            slot_obj = form.cleaned_data.get('slot')
            # slot_obj = Slot.objects.get(pk=slot_id)

            if slot_obj.disabled:
                messages.error(request, 'Slot not available!')
            else:  
                request_obj = form.save()
                message_title = 'Your session is confirmed! Make sure to attend the tutoring session on time.'
                message_text = ('Your tutor request has been '
                                'submitted and will be reviewed shortly.<br/>'
                                'Feedback reference code: <strong>{0}</strong><br/>').format(request_obj.feedback_ref)

                messages.success(request, message_title, extra_tags=message_text)
                
            # Reset the form.
            form = RequestForm()
    else:
        form = RequestForm()

    return render(request, 'home.html', {'form': form,
                                         'active_page': 'home', })


def about(request):
    """Displays a static about page."""

    return render(request, 'about.html', {'active_page': 'about', })
