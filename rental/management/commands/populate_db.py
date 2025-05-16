from django.core.management.base import BaseCommand
from django.db.utils import OperationalError
from rental.models import Vehicle, Location

class Command(BaseCommand):
    help = 'Заповнює базу даних початковими даними про транспорт та локації'

    def handle(self, *args, **kwargs):
        try:
            locations = [
                {'name': 'Центр', 'address': 'вул. Хрещатик, 1, Київ'},
                {'name': 'Поділ', 'address': 'вул. Сагайдачного, 25, Київ'},
                {'name': 'Оболонь', 'address': 'просп. Героїв Сталінграда, 10, Київ'},
            ]

            for location_data in locations:
                Location.objects.get_or_create(
                    name=location_data['name'],
                    defaults={'address': location_data['address']}
                )
                self.stdout.write(self.style.SUCCESS(f"Додано локацію {location_data['name']} до бази даних"))

            vehicles = [
                {
                    'name': 'Міський Круїзер',
                    'vehicle_type': 'bike',
                    'price_per_hour': 5.00,
                    'is_available': True,
                    'image': 'vehicles/city_cruiser.jpg',
                },
                {
                    'name': 'Гірський Мандрівник',
                    'vehicle_type': 'bike',
                    'price_per_hour': 7.50,
                    'is_available': True,
                    'image': 'vehicles/mountain_trekker.jpg',
                },
                {
                    'name': 'Електричний Зум',
                    'vehicle_type': 'scooter',
                    'price_per_hour': 10.00,
                    'is_available': True,
                    'image': 'vehicles/electric_zoom.jpg',
                },
                {
                    'name': 'Міський Скут',
                    'vehicle_type': 'scooter',
                    'price_per_hour': 8.00,
                    'is_available': True,
                    'image': 'vehicles/urban_scoot.jpg',
                },
                {
                    'name': 'Громовик 500',
                    'vehicle_type': 'motorcycle',
                    'price_per_hour': 20.00,
                    'is_available': True,
                    'image': 'vehicles/thunderbolt_500.jpg',
                },
                {
                    'name': 'Тіньовий Вершник',
                    'vehicle_type': 'motorcycle',
                    'price_per_hour': 25.00,
                    'is_available': True,
                    'image': 'vehicles/shadow_rider.jpg',
                },
            ]

            for vehicle_data in vehicles:
                Vehicle.objects.get_or_create(
                    name=vehicle_data['name'],
                    defaults={
                        'vehicle_type': vehicle_data['vehicle_type'],
                        'price_per_hour': vehicle_data['price_per_hour'],
                        'is_available': vehicle_data['is_available'],
                        'image': vehicle_data['image'],
                    }
                )
                self.stdout.write(self.style.SUCCESS(f"Додано {vehicle_data['name']} до бази даних"))

        except OperationalError as e:
            self.stdout.write(self.style.ERROR(
                f"Помилка: {e}. Переконайтеся, що міграції застосовані. Виконайте 'python manage.py makemigrations' та 'python manage.py migrate'."
            ))
            raise