from django import forms
from django.utils.translation import ugettext_lazy as _

from nocaptcha_recaptcha.fields import NoReCaptchaField

from .models import Request


class RequestForm(forms.ModelForm):
    captcha = NoReCaptchaField()

    class Meta:
        model = Request
        fields = ('student_id', 'student_name',
                  'student_phone_number', 'description', 'slot')
        labels = {
            'student_id': _('Student ID'),
            'student_name': _('Name'),
            'student_phone_number': _('Phone number'),
            'description': _('Notes'),
        }
        # help_texts = {
        #     'name': _('Some useful help text.'),
        # }
        error_messages = {
            'slot': {
                'required': _('Please select a slot.'),
                'invalid_choice': _('Slot was not recognized.'),
            },
        }
        widgets = {
            'slot': forms.HiddenInput(),
        }
