from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Booking, Payment

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Електронна пошта")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': 'Ім\'я користувача',
            'password1': 'Пароль',
            'password2': 'Підтвердження пароля',
        }

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['vehicle', 'location', 'start_time', 'end_time']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        labels = {
            'vehicle': 'Транспортний засіб',
            'location': 'Локація',
            'start_time': 'Час початку',
            'end_time': 'Час закінчення',
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        if start_time and end_time and end_time <= start_time:
            raise forms.ValidationError("Час закінчення має бути пізніше за час початку.")
        return cleaned_data

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['method']
        labels = {
            'method': 'Спосіб оплати',
        }