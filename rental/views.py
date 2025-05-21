from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, BookingForm, PaymentForm, ProfileForm
from .models import Vehicle, Booking, Payment, Profile, Location, Tariff, UserTariff
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            Profile.objects.create(user=user)
            messages.success(request, 'Реєстрація успішна!')
            return redirect(settings.ACCOUNT_SIGNUP_REDIRECT_URL)
    else:
        form = CustomUserCreationForm()
    return render(request, 'rental/register.html', {'form': form})

def map_view(request):
    pickup_points = Location.objects.all()
    return render(request, 'rental/map.html', {'pickup_points': pickup_points})

def pickup(request, point_id):
    request.session['selected_point_id'] = point_id
    selected_point = get_object_or_404(Location, id=point_id)
    return render(request, 'rental/pickup.html', {'selected_point': selected_point})

def vehicles(request, point_id):
    category = request.GET.get('category', '')
    vehicles = Vehicle.objects.filter(is_available=True)
    if category in ['bike', 'scooter', 'motorcycle']:
        vehicles = vehicles.filter(vehicle_type=category)
    categories = [
        ('', 'Усі', Vehicle.objects.filter(is_available=True).count()),
        ('bike', 'Велосипеди', Vehicle.objects.filter(vehicle_type='bike', is_available=True).count()),
        ('scooter', 'Скутери', Vehicle.objects.filter(vehicle_type='scooter', is_available=True).count()),
        ('motorcycle', 'Мотоцикли', Vehicle.objects.filter(vehicle_type='motorcycle', is_available=True).count()),
    ]
    return render(request, 'rental/vehicles.html', {
        'vehicles': vehicles,
        'categories': categories,
        'selected_category': category,
        'point_id': point_id,
    })

@login_required
def booking(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    location = get_object_or_404(Location, id=request.session.get('selected_point_id'))
    tariffs = Tariff.objects.all()
    user_tariffs = UserTariff.objects.filter(user=request.user, vehicle_type=vehicle.vehicle_type, location=location, tariff__is_subscription=True)
    active_tariff = user_tariffs.filter(tariff__name='Льготний проїзд (20 поїздок)', remaining_rides__gt=0).first() or \
                    user_tariffs.filter(tariff__name='Безліміт на місяць', expiry_date__gt=timezone.now()).first()

    form = BookingForm(initial={'vehicle': vehicle})
    if request.method == 'POST':
        if 'tariff_id' in request.POST:
            tariff_id = request.POST.get('tariff_id')
            tariff = get_object_or_404(Tariff, id=tariff_id)
            if tariff.is_subscription:
                user_tariff = UserTariff.objects.create(
                    user=request.user,
                    tariff=tariff,
                    vehicle_type=vehicle.vehicle_type,
                    location=location,
                    remaining_rides=tariff.max_rides if tariff.name == 'Льготний проїзд (20 поїздок)' else None,
                    expiry_date=timezone.now() + timedelta(days=tariff.duration_days) if tariff.name == 'Безліміт на місяць' else None
                )
                payment = Payment.objects.create(
                    user_tariff=user_tariff,
                    amount=tariff.price,
                    is_paid=False
                )
                messages.success(request, f'Ви обрали тариф: {tariff.name}')
                return redirect('payment_tariff', payment_id=payment.id)
            else:
                request.session['selected_tariff_id'] = tariff.id
                messages.success(request, f'Ви обрали тариф: {tariff.name}')
        elif 'book' in request.POST:
            tariff_id = request.session.get('selected_tariff_id')
            tariff = get_object_or_404(Tariff, id=tariff_id) if tariff_id else None
            if active_tariff:
                booking = Booking(user=request.user, vehicle=vehicle, location=location, tariff=active_tariff.tariff, total_price=0)
                if active_tariff.tariff.name == 'Льготний проїзд (20 поїздок)':
                    active_tariff.remaining_rides -= 1
                    active_tariff.save()
                booking.save()
                Payment.objects.create(booking=booking, amount=0, is_paid=True)
                messages.success(request, 'Бронювання успішне!')
                return redirect('my_bookings')
            elif tariff and (tariff.name == 'Оплата почасово' or tariff.name == 'Студентський гаманець'):
                form = BookingForm(request.POST)
                if form.is_valid():
                    booking = form.save(commit=False)
                    booking.user = request.user
                    booking.vehicle = vehicle
                    booking.location = location
                    booking.tariff = tariff
                    hours = (booking.end_time - booking.start_time).total_seconds() / 3600
                    if hours <= 0:
                        messages.error(request, 'Час закінчення має бути пізніше за час початку.')
                        return render(request, 'rental/booking.html', {
                            'form': form,
                            'vehicle': vehicle,
                            'tariffs': tariffs,
                            'selected_tariff': tariff,
                            'active_tariff': active_tariff,
                        })
                    booking.total_price = vehicle.price_per_hour * Decimal(str(hours))
                    if tariff.name == 'Студентський гаманець':
                        booking.total_price *= Decimal('0.5')  # Применяем скидку 50%
                    booking.save()
                    return redirect('payment', booking_id=booking.id)
            elif tariff:
                booking = Booking(user=request.user, vehicle=vehicle, location=location, tariff=tariff)
                booking.total_price = tariff.price if tariff.price else vehicle.price_per_hour * Decimal('1')
                if tariff.name == 'Студентський гаманець':
                    booking.total_price *= Decimal('0.5')
                booking.save()
                return redirect('payment', booking_id=booking.id)

    return render(request, 'rental/booking.html', {
        'form': form,
        'vehicle': vehicle,
        'tariffs': tariffs,
        'selected_tariff': get_object_or_404(Tariff, id=request.session.get('selected_tariff_id')) if request.session.get('selected_tariff_id') else None,
        'active_tariff': active_tariff,
    })

@login_required
def payment(request, booking_id=None, payment_id=None):
    if booking_id:
        booking = get_object_or_404(Booking, id=booking_id)
        payment = Payment.objects.create(booking=booking, amount=booking.total_price, is_paid=False)
    elif payment_id:
        payment = get_object_or_404(Payment, id=payment_id)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment.payment_method = form.cleaned_data['payment_method']
            payment.is_paid = True
            payment.save()
            messages.success(request, 'Оплата успішна!')
            return redirect('map')
    else:
        form = PaymentForm()
    return render(request, 'rental/payment.html', {'form': form, 'payment': payment})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-start_time')
    user_tariffs = UserTariff.objects.filter(user=request.user)
    bookings_with_details = [
        {
            'booking': booking,
            'is_paid': booking.payment_set.filter(is_paid=True).exists(),
            'location': booking.location.area if booking.location else 'Невідома локація',
            'tariff': booking.tariff.name if booking.tariff else 'Невідомий тариф',
        }
        for booking in bookings
    ]
    tariff_statuses = [
        {
            'tariff': ut.tariff,
            'vehicle_type': ut.vehicle_type,
            'location': ut.location.area,
            'remaining_rides': ut.remaining_rides if ut.tariff.name == 'Льготний проїзд (20 поїздок)' else None,
            'expiry_date': ut.expiry_date if ut.tariff.name == 'Безліміт на місяць' else None,
            'is_active': ut.is_active(),
        }
        for ut in user_tariffs
    ]
    return render(request, 'rental/my_bookings.html', {
        'bookings_with_details': bookings_with_details,
        'tariff_statuses': tariff_statuses,
    })

@login_required
def profile(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профіль оновлено!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'rental/profile.html', {'form': form})