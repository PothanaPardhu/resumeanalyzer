# core/forms.py
from django import forms
from .models import Resume, JobDescription
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ["file"]

class JobDescriptionForm(forms.ModelForm):
    class Meta:
        model = JobDescription
        fields = ["title", "text"]
        widgets = {"text": forms.Textarea(attrs={"rows": 6})}

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=False)
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
