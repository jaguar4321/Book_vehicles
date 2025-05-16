from django.contrib import admin
from .models import Vehicle, Booking, Payment, Location

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('name', 'vehicle_type', 'price_per_hour', 'is_available')
    list_filter = ('vehicle_type', 'is_available')
    search_fields = ('name',)

admin.site.register(Booking)
admin.site.register(Payment)
admin.site.register(Location)