from django import forms
from django.forms import DateInput
from .models import UserProfile

class OTPForm(forms.Form):
    email = forms.EmailField(label="Email", required=True)

class UserProfileForm(forms.ModelForm):
    dob = forms.DateField(widget=DateInput(attrs={'type': 'date'}))

    class Meta:
        model = UserProfile
        fields = ['name', 'father_name', 'age', 'dob', 'address', 'user_id_proof', 'photo']
