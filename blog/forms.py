from django import forms 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    password1 = forms.CharField(label="Password",widget=forms.PasswordInput(attrs={"class":"form-control"}))
    password2 = forms.CharField(label="Confirm Password (again)",widget=forms.PasswordInput(attrs={"class":"form-control"}))
    class Meta:
        model = User
        fields = ["username","first_name","last_name","email"]
        labels = {"first_name":"First Name","last_name":"Last Name","email":"Email"}
        widgets = {"username":forms.TextInput(attrs={"class":"form-control"}),
                   "first_name":forms.TextInput(attrs={"class":"form-control"}),
                   "last_name":forms.TextInput(attrs={"class":"form-control"}),
                   "email":forms.TextInput(attrs={"class":"form-control"}),
                   }