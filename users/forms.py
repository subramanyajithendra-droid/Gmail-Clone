from django import forms
from django.core.exceptions import ValidationError
from .models import User


class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'mobile', 'password']

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if mobile and not mobile.isdigit():
            raise ValidationError("Mobile number must be digits only")
        return mobile

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password")
        p2 = cleaned.get("confirm_password")

        if p1 != p2:
            raise ValidationError("Passwords do not match")

        return cleaned


class LoginForm(forms.Form):
    email_or_mobile = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
