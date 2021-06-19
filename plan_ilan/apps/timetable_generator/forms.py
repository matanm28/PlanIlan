from django import forms
from django.utils.translation import gettext_lazy as _

from plan_ilan.apps.web_site.models import Semester, Department


class FirstForm(forms.Form):
    name = forms.CharField(max_length=255, label='שם מערכת השעות', error_messages={'required': 'יא מזדיין שים שם תקין יא מניאק'})
    semester = forms.ModelChoiceField(Semester.objects.all(), label='סמסטר', error_messages={'required': 'נא לבחור סמסטר'})
    max_num_of_days = forms.IntegerField(min_value=1, max_value=6, label='מספר ימי לימוד',
                                         error_messages={'required': 'יש לבחור כמות ימים בין 1 ל-6'})


class DepartmentsForm(forms.Form):
    departments = forms.ModelMultipleChoiceField(Department.objects.all().order_by('label'), label='בחר מחלקות',
                                                 widget=forms.CheckboxSelectMultiple)
