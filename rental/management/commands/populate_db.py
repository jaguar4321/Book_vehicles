from django.core.management.base import BaseCommand
from django.db.utils import OperationalError
from django.utils import timezone
from datetime import timedelta
from rental.models import Vehicle, Location, Tariff, UserTariff
from django.contrib.auth.models import User
from django.conf import settings

class Command(BaseCommand):
    help = 'Заповнює базу даних початковими даними про транспорт, локації, тарифи та користувацькі тарифи'

    def handle(self, *args, **kwargs):
        try:
            # Переконаємося, що суперкористувач існує для зв'язків UserTariff
            if not User.objects.filter(is_superuser=True).exists():
                User.objects.create_superuser(
                    username='admin',
                    email='admin@example.com',
                    password='admin'
                )
                self.stdout.write(self.style.SUCCESS('Створено суперкористувача admin з паролем admin'))

            # Дані для Vehicle
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

            # Додавання транспортних засобів
            for vehicle_data in vehicles:
                vehicle, created = Vehicle.objects.get_or_create(
                    name=vehicle_data['name'],
                    defaults={
                        'vehicle_type': vehicle_data['vehicle_type'],
                        'price_per_hour': vehicle_data['price_per_hour'],
                        'is_available': vehicle_data['is_available'],
                        'image': vehicle_data['image'],
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Додано {vehicle_data['name']} до бази даних"))
                else:
                    self.stdout.write(self.style.WARNING(f"{vehicle_data['name']} вже існує в базі даних"))

            # Дані для Location
            locations = [
                {
                    'name': 'Пункт 1 - Центр',
                    'area': 'Центральний район Харкова',
                    'lat': 49.9935,
                    'lon': 36.2304,
                },
                {
                    'name': 'Пункт 2 - Салтівка',
                    'area': 'Салтівський район',
                    'lat': 49.9903,
                    'lon': 36.2801,
                },
                {
                    'name': 'Пункт 3 - Північна Салтівка',
                    'area': 'Північні райони Харкова',
                    'lat': 50.0300,
                    'lon': 36.2600,
                },
            ]

            # Додавання локацій
            for location_data in locations:
                location, created = Location.objects.get_or_create(
                    name=location_data['name'],
                    defaults={
                        'area': location_data['area'],
                        'lat': location_data['lat'],
                        'lon': location_data['lon'],
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Додано {location_data['name']} до бази даних"))
                else:
                    self.stdout.write(self.style.WARNING(f"{location_data['name']} вже існує в базі даних"))

            # Дані для Tariff
            tariffs = [
                {
                    'name': 'Льготний проїзд (20 поїздок)',
                    'price': 200.00,
                    'description': 'Фіксована ціна на 20 поїздок, не горять.',
                    'is_subscription': True,
                    'max_rides': 20,
                    'duration_days': None,
                },
                {
                    'name': 'Безліміт на місяць',
                    'price': 800.00,
                    'description': 'Необмежена кількість поїздок протягом місяця.',
                    'is_subscription': True,
                    'max_rides': None,
                    'duration_days': 30,
                },
                {
                    'name': 'Студентський гаманець',
                    'price': None,
                    'description': '50% знижка.',
                    'is_subscription': False,
                    'max_rides': None,
                    'duration_days': None,
                },
                {
                    'name': 'Оплата почасово',
                    'price': None,
                    'description': 'Оплата залежить від часу використання.',
                    'is_subscription': False,
                    'max_rides': None,
                    'duration_days': None,
                },
            ]

            # Додавання тарифів
            for tariff_data in tariffs:
                tariff, created = Tariff.objects.get_or_create(
                    name=tariff_data['name'],
                    defaults={
                        'price': tariff_data['price'],
                        'description': tariff_data['description'],
                        'is_subscription': tariff_data['is_subscription'],
                        'max_rides': tariff_data['max_rides'],
                        'duration_days': tariff_data['duration_days'],
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Додано {tariff_data['name']} до бази даних"))
                else:
                    self.stdout.write(self.style.WARNING(f"{tariff_data['name']} вже існує в базі даних"))

            # Дані для UserTariff (приклади для тестування)
            user_tariff_data = [
                {
                    'user': User.objects.get(username='admin'),
                    'tariff': Tariff.objects.get(name='Льготний проїзд (20 поїздок)'),
                    'vehicle_type': 'bike',
                    'location': Location.objects.get(name='Пункт 1 - Центр'),
                    'remaining_rides': 15,
                    'expiry_date': None,
                },
                {
                    'user': User.objects.get(username='admin'),
                    'tariff': Tariff.objects.get(name='Безліміт на місяць'),
                    'vehicle_type': 'scooter',
                    'location': Location.objects.get(name='Пункт 2 - Салтівка'),
                    'remaining_rides': None,
                    'expiry_date': timezone.now() + timedelta(days=15),
                },
            ]

            # Додавання користувацьких тарифів
            for ut_data in user_tariff_data:
                user_tariff, created = UserTariff.objects.get_or_create(
                    user=ut_data['user'],
                    tariff=ut_data['tariff'],
                    vehicle_type=ut_data['vehicle_type'],
                    location=ut_data['location'],
                    defaults={
                        'remaining_rides': ut_data['remaining_rides'],
                        'expiry_date': ut_data['expiry_date'],
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Додано UserTariff для {ut_data['user'].username} - {ut_data['tariff'].name}"))
                else:
                    self.stdout.write(self.style.WARNING(f"UserTariff для {ut_data['user'].username} - {ut_data['tariff'].name} вже існує"))

            self.stdout.write(self.style.SUCCESS('База даних успішно заповнена початковими даними!'))

        except OperationalError as e:
            self.stdout.write(self.style.ERROR(
                f"Помилка: {e}. Переконайтеся, що міграції застосовані. Виконайте 'python manage.py makemigrations' та 'python manage.py migrate'."
            ))
            raise
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("Помилка: Користувач 'admin' не знайдений. Створіть суперкористувача спочатку."))
            raise
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Несподівана помилка: {e}"))
            raise
