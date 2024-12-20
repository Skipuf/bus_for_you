from django.core.management.base import BaseCommand
from database.models import CustomUser, Client, Carrier, Docs, Transport


class Command(BaseCommand):
    help = 'Создание 2 клиентов и 2 транспортных компаний с подтвержденными документами'

    def handle(self, *args, **kwargs):
        try:  # Создание пользователей
            user1 = CustomUser.objects.create_user(  # изменено на CustomUser
                email='client1@example.com',
                password='password123',
                first_name='Иван',
                last_name='Иванов',
                surname='Иванович',
                is_active=True
            )

            user2 = CustomUser.objects.create_user(  # изменено на CustomUser
                email='client2@example.com',
                password='password123',
                first_name='Петр',
                last_name='Петров',
                surname='Петрович',
                is_active=True
            )

            # Создание клиентов
            client1 = Client.objects.create(
                user=user1,
                client_type='IND',
                phone_number='1234567890',
                # group='Client' убрал, такого поля нет в базе
            )

            client2 = Client.objects.create(
                user=user2,
                client_type='LEG',
                legal_type='LLC',
                company_name='ООО Пример',
                inn='1234567890',
                phone_number='0987654321',
                # group='Client' убрал, такого поля нет в базе
            )

            # Создание пользователей для транспортных компаний
            user3 = CustomUser.objects.create_user(  # изменено на CustomUser
                email='carrier1@example.com',
                password='password123',
                first_name='Сергей',
                last_name='Сергеев',
                is_active=True
            )

            user4 = CustomUser.objects.create_user(  # изменено на CustomUser
                email='carrier2@example.com',
                password='password123',
                first_name='Анна',
                last_name='Антонова',
                is_active=True
            )

            # Создание документов
            # doc1 = Docs.objects.create(
            #     licence=b'',
            #     medical_examination=b'',
            #     insurance=b'',
            #     contract=b'',
            #     validation=True
            # )
            #
            # doc2 = Docs.objects.create(
            #     licence=b'',
            #     medical_examination=b'',
            #     insurance=b'',
            #     contract=b'',
            #     validation=True
            # )

            # Создание транспортных компаний
            carrier1 = Carrier.objects.create(
                user=user3,
                carrier_type='LLC',
                company_name='ТК Пример 1',
                inn='0987654321',
                phone_number='1112223333',
                # docs=doc1,
                # group='Carrier' убрал, такого поля нет в базе
            )

            carrier2 = Carrier.objects.create(
                user=user4,
                carrier_type='GP',
                company_name='ТК Пример 2',
                inn='2345678901',
                phone_number='4445556666',
                # docs=doc2,                # group='Carrier' убрал, такого поля нет в базе
            )

            self.stdout.write(self.style.SUCCESS('Успешно создано 2 клиента и 2 транспортные компании.'))

        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Ошибка: {e}'))
