from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _

from nocaptcha_recaptcha.fields import NoReCaptchaField

from .models import Feedback, Request


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
        help_texts = {
            'description': _('Mention any alternative slots, topics needed to cover, etc.'),
        }
        error_messages = {
            'slot': {
                'required': _('Please select a slot.'),
                'invalid_choice': _('Slot was not recognized.'),
            },
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 15}),
            'slot': forms.HiddenInput(),
        }


class RequestFeedbackRefField(forms.Form):
    reference_code = forms.CharField(max_length=10)

    def clean_reference_code(self):
        reference_code = self.cleaned_data.get('reference_code').upper()

        try:
            Request.objects.get(feedback_ref=reference_code)
        except ObjectDoesNotExist:
            raise forms.ValidationError('Failed to identify reference code.')

        return reference_code


class FeedbackForm(forms.ModelForm):
    captcha = NoReCaptchaField()

    class Meta:
        model = Feedback
        fields = ('satisfaction', 'description',)
        labels = {
            'description': _('Comment'),
        }
