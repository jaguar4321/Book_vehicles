from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.vehicle_list, name='vehicle_list'),
    path('book/<int:vehicle_id>/', views.book_vehicle, name='book_vehicle'),
    path('payment/<int:booking_id>/', views.payment, name='payment'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
]