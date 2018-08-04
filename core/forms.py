from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist


from nocaptcha_recaptcha.fields import NoReCaptchaField

from .models import Request, Feedback


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


class RequestFeedbackRefField(forms.Form):
    feedback_ref = forms.CharField(max_length=10)

    def clean_feedback_ref(self):
        feedback_ref = self.cleaned_data.get('feedback_ref').upper()

        try:
            Request.objects.get(feedback_ref=feedback_ref)
        except ObjectDoesNotExist:
            raise forms.ValidationError('Not found')

        return feedback_ref


class FeedbackForm(forms.ModelForm):
    captcha = NoReCaptchaField()

    class Meta:
        model = Feedback
        fields = ('satisfaction', 'description',)
        labels = {
            'description': _('Comment'),
        }
