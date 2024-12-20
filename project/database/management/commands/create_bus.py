from django.core.management.base import BaseCommand
from database.models import Transport, Route, Cities, Schedule
import random
import datetime


class Command(BaseCommand):
    help = 'Создает карточку автобуса'

    def handle(self, *args, **kwargs):
        try:
            route1 = Route.objects.create(
                id_to=Cities.objects.all()[random.randint(1, 1000)],
                id_from=Cities.objects.first()
            )

            transport1 = Transport.objects.create(
                bus_nickname='Автобус',
                brand='Temsa',
                model='Maraton 13 VIP',
                year_issued=2019,
                n_deck=53,
                n_seats=55,
                photo=b'',
                luggage=True,
                wifi=True,
                tv=True,
                toilet=False,
                rating=0,
                id_route=route1,

            )

            schedule1 = Schedule.objects.create(
                bus_id=transport1,
                trip_start=datetime.datetime.now() + datetime.timedelta(days=1),
                trip_end=datetime.datetime.now() + datetime.timedelta(days=1, hours=4),
            )

            self.stdout.write(self.style.SUCCESS('Успешно создан автобус.'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Ошибка: {e}'))
