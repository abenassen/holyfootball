from django import forms

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = YourModelName
        widgets = {
            'username' : forms.TextInput(attrs = {'placeholder': 'Username'}),
            'email'    : forms.TextInput(attrs = {'placeholder': 'E-Mail'}),
        }


