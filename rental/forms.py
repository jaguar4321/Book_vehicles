from django import forms
from django.contrib.auth.models import User
from .models import Profile, Booking, Payment

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'bio', 'phone']

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['start_time', 'end_time']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_time'].widget = forms.DateTimeInput(attrs={'type': 'datetime-local'})
        self.fields['end_time'].widget = forms.DateTimeInput(attrs={'type': 'datetime-local'})
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_method']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_method'].widget = forms.Select(choices=self.fields['payment_method'].choices)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})