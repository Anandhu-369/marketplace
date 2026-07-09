from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from traders.models import *

class SignupForm(UserCreationForm):
    class Meta:
        model=User
        fields=["first_name","last_name","username","email","password1","password2"]

class SigninForm(forms.Form):
    username=forms.CharField(widget=forms.TextInput(attrs={"class":"w-full px-1 py-1 border rounded bg-white"}))
    password=forms.CharField(widget=forms.PasswordInput(attrs={"class":"w-full px-1 py-1 border rounded bg-white"}))

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "product_type","title","description","price","starting_bid","category","is_negotiatable","auction_start", "auction_end",]
        widgets = {"auction_start": forms.DateTimeInput(attrs={"type": "datetime-local","class": "w-full rounded-lg border border-gray-300 px-4 py-3 focus:ring-2 focus:ring-indigo-500",},format="%Y-%m-%dT%H:%M",),

            "auction_end": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "w-full rounded-lg border border-gray-300 px-4 py-3 focus:ring-2 focus:ring-indigo-500",
                },
                format="%Y-%m-%dT%H:%M",
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["auction_start"].input_formats = [
            "%Y-%m-%dT%H:%M"
        ]

        self.fields["auction_end"].input_formats = [
            "%Y-%m-%dT%H:%M"
        ]

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["phone","address","image","latitude","longitude",]
        widgets = {
            "phone": forms.TextInput(attrs={
                "class": "w-full border rounded-lg p-3 focus:ring-2 focus:ring-blue-500",
                "placeholder": "Enter phone number",
            }),
            "address": forms.Textarea(attrs={
                "class": "w-full border rounded-lg p-3 focus:ring-2 focus:ring-blue-500",
                "rows": 3,
                "placeholder": "Enter address",
            }),
            "image": forms.ClearableFileInput(attrs={
                "class": "w-full border rounded-lg p-2",
            }),
            "latitude": forms.NumberInput(attrs={
                "class": "w-full border rounded-lg p-3 focus:ring-2 focus:ring-blue-500",
                "placeholder": "Latitude",
                "step": "any",
            }),
            "longitude": forms.NumberInput(attrs={
                "class": "w-full border rounded-lg p-3 focus:ring-2 focus:ring-blue-500",
                "placeholder": "Longitude",
                "step": "any",
            }),
        }