from django import forms


class UserCreationForm(forms.Form):
    '''
    Sign-up form

    '''
    handle = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField()
     
