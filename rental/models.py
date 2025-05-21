from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Vehicle(models.Model):
    name = models.CharField(max_length=100)
    vehicle_type = models.CharField(max_length=20, choices=[('bike', 'Велосипед'), ('scooter', 'Скутер'), ('motorcycle', 'Мотоцикл')])
    price_per_hour = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='vehicles/', null=True, blank=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.vehicle_type})"

class Location(models.Model):
    name = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    lat = models.FloatField()
    lon = models.FloatField()

    def __str__(self):
        return self.name

class Tariff(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField()
    is_subscription = models.BooleanField(default=False)
    max_rides = models.IntegerField(null=True, blank=True)
    duration_days = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

class UserTariff(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tariff = models.ForeignKey(Tariff, on_delete=models.CASCADE)
    vehicle_type = models.CharField(max_length=20, choices=[('bike', 'Велосипед'), ('scooter', 'Скутер'), ('motorcycle', 'Мотоцикл')])
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)
    remaining_rides = models.IntegerField(null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)

    def is_active(self):
        if self.tariff.name == 'Безліміт на місяць':
            return self.expiry_date > timezone.now()
        elif self.tariff.name == 'Льготний проїзд (20 поїздок)':
            return self.remaining_rides > 0
        return True

    def __str__(self):
        return f"{self.user.username} - {self.tariff.name} ({self.vehicle_type}, {self.location.name})"

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True)
    tariff = models.ForeignKey(Tariff, on_delete=models.SET_NULL, null=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Booking {self.id} by {self.user.username}"

class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True)
    user_tariff = models.ForeignKey(UserTariff, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    payment_method = models.CharField(
        max_length=20,
        choices=[('cash', 'Нал'), ('card', 'Карта')],
        default='card'
    )

    def __str__(self):
        return f"Payment {self.id} for {self.booking or self.user_tariff}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.user.username