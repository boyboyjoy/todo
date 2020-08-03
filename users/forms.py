from django import forms


class SignUpForm(forms.Form):
    username = forms.CharField(max_length=50)
    email = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    moderator = forms.BooleanField(widget=forms.CheckboxInput, required=False)


class FormLogin(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
