from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class SignupForm(UserCreationForm):
    class Meta:
        model=User
        fields=["first_name","last_name","username","email","password1","password2"]

class SigninForm(forms.Form):
    username=forms.CharField(widget=forms.TextInput(attrs={"class":"w-full px-1 py-1 border rounded bg-white"}))
    password=forms.CharField(widget=forms.PasswordInput(attrs={"class":"w-full px-1 py-1 border rounded bg-white"}))