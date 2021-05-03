from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User as DjangoUser

from PlanIlan.models import Faculty, Account


class CreateDjangoUserForm(UserCreationForm):
    class Meta:
        model = DjangoUser
        fields = ['username', 'password1', 'password2', 'first_name', 'last_name', 'email']


class CreateAccountForm(forms.ModelForm):
    faculty = forms.ModelChoiceField(queryset=Faculty.objects, required=True, label='Faculty', to_field_name='label')

    class Meta:
        model = Account
        fields = ['faculty', 'email']
