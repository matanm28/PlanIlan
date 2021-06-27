from django import forms
from django.forms.utils import ErrorList

from plan_ilan.apps.web_site.models import Semester, Department


class FirstForm(forms.Form):
    name = forms.CharField(max_length=255, label='שם מערכת השעות',
                           error_messages={'required': 'נא הכנס שם תקין'},
                           widget=forms.TextInput(attrs={'placeholder': 'שם מערכת שעות...'}))
    semester = forms.ModelChoiceField(Semester.objects.all(), label='סמסטר', empty_label="סמסטר...",
                                      error_messages={'required': 'נא לבחור סמסטר'})
    max_num_of_days = forms.IntegerField(min_value=1, max_value=6, label='מספר ימי לימוד',
                                         error_messages={'required': 'יש לבחור כמות ימים בין 1 ל-6'},
                                         widget=forms.NumberInput(
                                             attrs={'placeholder': "...מס' ימי לימוד",
                                                    'style': 'width:14ch; text-align: center'}))


class DepartmentsForm(forms.Form):
    departments = forms.ModelMultipleChoiceField(Department.with_courses().order_by('label'), label='בחר מחלקות',
                                                 widget=forms.CheckboxSelectMultiple)

    def __init__(self, accept_empty=False, data=None, files=None, auto_id='id_%s', prefix=None, initial=None,
                 error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, field_order=None, use_required_attribute=None,
                 renderer=None):
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, field_order,
                         use_required_attribute, renderer)
        self.fields['departments'].required = not accept_empty
