from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

from rental_project import settings
from .forms import CustomUserCreationForm, BookingForm, PaymentForm
from .models import Vehicle, Booking, Payment
from django.contrib import messages
from decimal import Decimal
from django.contrib.auth import logout as auth_logout

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Реєстрація успішна!')
            return redirect(settings.ACCOUNT_SIGNUP_REDIRECT_URL)
    else:
        form = CustomUserCreationForm()
    return render(request, 'rental/register.html', {'form': form})

def vehicle_list(request):
    category = request.GET.get('category', '')
    if category in ['bike', 'scooter', 'motorcycle']:
        vehicles = Vehicle.objects.filter(vehicle_type=category, is_available=True)
    else:
        vehicles = Vehicle.objects.filter(is_available=True)
    categories = [
        ('', 'Усі', Vehicle.objects.filter(is_available=True).count()),
        ('bike', 'Велосипеди', Vehicle.objects.filter(vehicle_type='bike', is_available=True).count()),
        ('scooter', 'Скутери', Vehicle.objects.filter(vehicle_type='scooter', is_available=True).count()),
        ('motorcycle', 'Мотоцикли', Vehicle.objects.filter(vehicle_type='motorcycle', is_available=True).count()),
    ]
    return render(request, 'rental/vehicle_list.html', {'vehicles': vehicles, 'categories': categories, 'selected_category': category})

@login_required
def book_vehicle(request, vehicle_id):
    vehicle = Vehicle.objects.get(id=vehicle_id)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.vehicle = vehicle
            hours = (booking.end_time - booking.start_time).total_seconds() / 3600
            booking.total_price = vehicle.price_per_hour * Decimal(str(hours))
            booking.save()
            messages.success(request, 'Бронювання успішне! Перейдіть до оплати.')
            return redirect('payment', booking_id=booking.id)
    else:
        form = BookingForm(initial={'vehicle': vehicle})
    return render(request, 'rental/book_vehicle.html', {'form': form, 'vehicle': vehicle})

@login_required
def payment(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.booking = booking
            payment.amount = booking.total_price
            payment.is_paid = True
            payment.save()
            messages.success(request, 'Оплата успішна!')
            return redirect('vehicle_list')
    else:
        form = PaymentForm()
    return render(request, 'rental/payment.html', {'form': form, 'booking': booking})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-start_time')
    return render(request, 'rental/my_bookings.html', {'bookings': bookings})
