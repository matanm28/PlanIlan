from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import User
from django import forms


class CreateUserForm(UserCreationForm):
    faculty = forms.CharField(required=True, label='Faculty')
    first_name = forms.CharField(required=True, label='First Name')
    last_name = forms.CharField(required=True, label='Last Name')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'faculty']
