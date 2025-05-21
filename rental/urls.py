from django.urls import path
from . import views

urlpatterns = [
    path('', views.map_view, name='map'),
    path('pickup/<int:point_id>/', views.pickup, name='pickup'),
    path('vehicles/<int:point_id>/', views.vehicles, name='vehicles'),
    path('booking/<int:vehicle_id>/', views.booking, name='booking'),
    path('payment/<int:booking_id>/', views.payment, name='payment'),
    path('payment/tariff/<int:payment_id>/', views.payment, name='payment_tariff'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
]