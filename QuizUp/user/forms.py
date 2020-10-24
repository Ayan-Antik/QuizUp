from django import forms


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()


class SignUpForm(forms.Form):
    username = forms.CharField()
    dob = forms.DateField()
    email = forms.EmailField()
    password1 = forms.CharField()
    password2 = forms.CharField()

