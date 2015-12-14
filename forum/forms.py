from django import forms

from nocaptcha_recaptcha.fields import NoReCaptchaField


class RegistrationForm(forms.Form):
    username = forms.CharField(label='username', max_length=100)
    password = forms.CharField(label='password', max_length=100)
    email = forms.CharField(label='email', max_length=100)
    captcha = NoReCaptchaField()