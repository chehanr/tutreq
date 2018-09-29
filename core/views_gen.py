import csv

from django.contrib.admin.views.decorators import staff_member_required
from django.http import StreamingHttpResponse
from django.utils import timezone
from easy_pdf.rendering import render_to_pdf_response

from .models import Request
from .utils import get_request_item_dict, get_request_items_dict


@staff_member_required
def generate_pdf(request):
    """Generates a pdf file specific request object."""

    request_id = request.GET.get('request-id')
    request_obj = Request.objects.get(pk=request_id)
    request_item = get_request_item_dict(request_obj)
    gen_date_time = timezone.now()

    template = 'pdf_template.html'
    context = {'request': request_item, 'generated_date_time': gen_date_time}
    pdf_filename = 'tutreq_request_r-{}.pdf'.format(request_item['id'])

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
def generate_csv(request):
    """Generates a csv file with all (or specific `request_id`) request object(s)."""

    request_id = request.GET.get('request-id')
    request_items_dict = get_request_items_dict(request_id)
    rows = []

    row_header = (
        'Request ID', 'Request identifier', 'Request made on',
        'Student ID', 'Student name', 'Student phone number',
        'Request dismissed status', 'Request dismissed/ relodged time',
        'Request archived status', 'Request archived/ unarchavied time', 'Request notes',
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
            request_item['dismissed'], request_item['dismiss_relodge_date_time'],
            request_item['archived'], request_item['archive_unarchive_date_time'], request_item['description'],
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
    if request_id:
        csv_filename = 'tutreq_log_r-{}.csv'.format(request_id)

    response['Content-Disposition'] = 'attachment; filename="{}"'.format(
        csv_filename)

    return response
