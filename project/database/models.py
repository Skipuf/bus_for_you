from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import DateTimeRangeField
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinLengthValidator
from .managers import CustomUserManager

CLIENT_TYPE = [
    ('IND', 'Физичекое лицо'),
    ('LEG', 'Юридическое лицо')
]

LEGAL_TYPE = [
    (None, '---------'),
    ('GP', 'Полное товарищество'),
    ('LP', 'Товарищество на вере (коммандитное товарищество)'),
    ('EC', 'Хозяйственное общество'),
    ('PJC', 'Публичное акционерное общество'),
    ('NJC', 'Непубличное акционерное общество'),
    ('LLC', 'Общество с ограниченной ответственностью'),
    ('IE', 'Индивидуальный предприниматель'),
    ('UE', 'Унитарное предприятие'),
    ('FD', 'Фонд'),
    ('EST', 'Учреждение'),
    ('OTH', 'Другое'),
]


DOC_TYPE = [
    ('LC', 'Licence'),
    ('ME', 'Medical examination'),
    ('IS', 'Insurance'),
    ('CT', 'Contract'),
]


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    surname = models.CharField(_('surname'), max_length=30, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    photo = models.ImageField(upload_to='images/', blank=True,
                              null=True)  # в default надо загрузить стандартную картинку, а null - убрать
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Client(models.Model):
    client_type = models.CharField(max_length=3, choices=CLIENT_TYPE, default='IND')
    legal_type = models.CharField(max_length=255, choices=LEGAL_TYPE, default=None, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    inn = models.CharField(blank=True, null=True)
    kpp = models.CharField(blank=True, null=True)
    ogrn = models.CharField(blank=True, null=True)
    current_account = models.CharField(blank=True, null=True)
    corresp_account = models.CharField(blank=True, null=True)
    bik = models.CharField(blank=True, null=True)
    oktmo = models.CharField(blank=True, null=True)
    legal_address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(blank=True, null=True)

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)


class Carrier(models.Model):
    carrier_type = models.CharField(max_length=255, choices=LEGAL_TYPE, default='GP')
    company_name = models.CharField(max_length=255)
    create_time = models.DateTimeField(auto_now_add=True)
    inn = models.CharField()
    kpp = models.CharField()
    ogrn = models.CharField(blank=True, null=True)
    current_account = models.CharField(blank=True, null=True)
    corresp_account = models.CharField(blank=True, null=True)
    bik = models.CharField(blank=True, null=True)
    oktmo = models.CharField(blank=True, null=True)
    legal_address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(blank=True, null=True)
    rating = models.IntegerField(default=0)

    id_transport = models.ForeignKey('Transport', blank=True, null=True, on_delete=models.CASCADE)
    id_extra_service = models.ForeignKey('ExtraService', blank=True, null=True, on_delete=models.CASCADE)
    id_route = models.ForeignKey('Route', blank=True, null=True, on_delete=models.CASCADE)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    # тут будет функция по подсчёту среднего рейтинга из всех отзывов на все автобусы.


class Docs(models.Model):
    document = models.FileField(upload_to='documents/')
    doc_type = models.CharField(max_length=2, choices=DOC_TYPE, default='LC')
    validation = models.BooleanField(default='False')

    id_carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE)


class Comment(models.Model):
    text = models.TextField()
    answer = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    id_order = models.OneToOneField('Order', on_delete=models.CASCADE)
    id_client = models.ForeignKey(Client, on_delete=models.CASCADE)
    id_carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE)


class Cities(models.Model):
    name = models.CharField(max_length=255)
    region = models.CharField(max_length=255)


class Route(models.Model):
    id_from = models.OneToOneField(Cities, on_delete=models.CASCADE, related_name='routes_from')
    id_to = models.OneToOneField(Cities, on_delete=models.CASCADE, related_name='routes_to')


class ExtraService(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    price = models.IntegerField(default=0)


class TransportQuerySet(models.QuerySet):  # позволяет проверять доступность автобуса в заданный временной промежуток.
    def available(self, start_date, end_date):
        return self.exclude(
            schedule__trip_start__lt=end_date,
            schedule__trip_end__gt=start_date
        )


class TransportQuerySet(models.QuerySet):  # позволяет проверять доступность автобуса в заданный временной промежуток.
    def available(self, start_date, end_date):
        return self.exclude(
            schedule__trip_start__lt=end_date,
            schedule__trip_end__gt=start_date
        )


class Transport(models.Model):
    bus_nickname = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    year_issued = models.IntegerField(default=0)
    n_deck = models.IntegerField(default=0)
    n_seats = models.IntegerField(default=0)
    photo = models.BinaryField(editable=False)
    luggage = models.BooleanField(default=False)
    wifi = models.BooleanField(default=False)
    tv = models.BooleanField(default=False)
    toilet = models.BooleanField(default=False)

    rating = models.IntegerField(default=0)
    id_route = models.ForeignKey(Route, on_delete=models.CASCADE)
    objects = TransportQuerySet.as_manager()

    # тут будет функция по подсчёту среднего рейтинга из всех заказов на этот автобус.


class Schedule(models.Model):
    bus_id = models.ForeignKey(Transport, on_delete=models.CASCADE)
    trip_start = models.DateTimeField()
    trip_end = models.DateTimeField()


class Order(models.Model):
    status = models.CharField(max_length=255, choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
        ('completed', 'Completed'),
    ], default='pending')
    create_time = models.DateTimeField(auto_now_add=True)
    time_range = DateTimeRangeField()
    passenger_type = models.CharField(max_length=255, choices=[
        ('children', 'Children'),
        ('adults', 'Adults'),
        ('mixed', 'Mixed'),
        ('corporate', 'Corporate'),
    ], default='mixed')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notification_sent = models.BooleanField(default=False)

    id_extra_service = models.ForeignKey(ExtraService, blank=True, null=True, on_delete=models.CASCADE)
    id_client = models.ForeignKey(Client, on_delete=models.CASCADE)
    id_transport = models.ForeignKey(Transport, on_delete=models.CASCADE)
    id_route = models.ForeignKey(Route, on_delete=models.CASCADE)
    id_carrier = models.OneToOneField(Carrier, on_delete=models.CASCADE)

    def __str__(self):
        return f"Order {self.pk} - {self.status}"

    def is_conflicting(self):
        conflicting = Order.objects.filter(
            id_transport=self.id_transport,
            time_range__overlap=self.time_range,
            status__in=['pending', 'confirmed']
        ).exclude(id=self.id)
        return conflicting.exists()


class Comment(models.Model):
    text = models.TextField()
    answer = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    id_order = models.OneToOneField(Order, on_delete=models.CASCADE)
    id_client = models.ForeignKey(Client, on_delete=models.CASCADE)
    id_carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE)


class Mailing(models.Model):
    id = models.AutoField(primary_key=True)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    send_time = models.DateTimeField()  # время отправки
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_sent = models.BooleanField(default=False)
    task_id = models.CharField(max_length=255, blank=True, null=True)
    failed_recipients = models.TextField(blank=True, null=True)
    mailing_type = models.CharField(max_length=50, choices=[
        ('notification', 'Notification'),
        ('promotion', 'Promotion'),
        ('reminder', 'Reminder'),
    ], default='notification')
    
    def __str__(self):
        return self.subject


class Subscription(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE)
    subscribed = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['user', 'mailing']


class Notification(models.Model):
    booking = models.ForeignKey(Order, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=20, choices=[
        ('reminder', 'Reminder'),
        ('status', 'Status'),
        ('custom', 'Custom'),
    ])
    message = models.TextField()
    read_status = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Notification for Booking {self.booking.id} - {self.type}"
