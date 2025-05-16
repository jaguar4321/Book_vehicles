from django.db import models
from django.contrib.auth.models import User

class Location(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name} ({self.address})"

class Vehicle(models.Model):
    TYPE_CHOICES = [
        ('bike', 'Велосипед'),
        ('scooter', 'Скутер'),
        ('motorcycle', 'Мотоцикл'),
    ]
    name = models.CharField(max_length=100)
    vehicle_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    price_per_hour = models.DecimalField(max_digits=6, decimal_places=2)
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='vehicles/', null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.vehicle_type})"

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    total_price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.user.username} - {self.vehicle.name} - {self.location.name}"

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('card', 'Картка'),
        ('cash', 'Готівка при отриманні'),
    ]
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Оплата для {self.booking}"