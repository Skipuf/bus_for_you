from datetime import timedelta

from celery import shared_task, group
from django.core.mail import send_mail, BadHeaderError
from django.core.cache import cache
from django.utils.timezone import now

from database.models import Mailing, Subscription, Order, Schedule


@shared_task(bind=True, max_retries=3)
def send_email_batch(self, mailing_id, batch):
    # Отправка пакета писем
    failed_recipients = []
    try:
        mailing = Mailing.objects.get(id=mailing_id)
    except Mailing.DoesNotExist:
        raise ValueError(f"Mailing with id {mailing_id} does not exist.")

    for email in batch:
        try:
            send_mail(
                subject=mailing.subject,
                message=mailing.body,
                from_email="noreply@example.com",
                recipient_list=[email],
                fail_silently=False,
            )
        except BadHeaderError:
            failed_recipients.append(email)
        except Exception as exc:
            raise self.retry(exc=exc, countdown=60)

    if failed_recipients:
        mailing.failed_recipients = (mailing.failed_recipients or "") + ", ".join(failed_recipients) + ";"
        mailing.save()

    return f"Batch of {len(batch)} emails sent."


@shared_task(bind=True)
def send_notification(self, mailing_id):
    # Планирование уведомлений и отправка пакетов
    try:
        mailing = Mailing.objects.get(id=mailing_id)
    except Mailing.DoesNotExist:
        raise ValueError(f"Mailing with id {mailing_id} does not exist.")

    cache_key = f"mailing_subscriptions_{mailing_id}"
    subscriptions = cache.get(cache_key)
    if not subscriptions:
        subscriptions = list(
            Subscription.objects.filter(mailing=mailing, subscribed=True)
            .values_list("user__email", flat=True)
        )
        cache.set(cache_key, subscriptions, timeout=60 * 10)  # Кэшируем на 10 минут

    if not subscriptions:
        mailing.failed_recipients = "No recipients found."
        mailing.save()
        return "No recipients to send the notification."

    batch_size = 100
    tasks = [
        send_email_batch.s(mailing_id, subscriptions[i : i + batch_size])
        for i in range(0, len(subscriptions), batch_size)
    ]
    group(tasks).apply_async()

    mailing.is_sent = True
    mailing.save()
    return f"Notification tasks for {len(subscriptions)} recipients created."


@shared_task
def send_booking_notifications():
    # Уведомление о бронировании, которое наступит через 24 часа и не имеет другого уведомления
    future_schedules = Schedule.objects.filter(
        trip_start__range=(now(), now() + timedelta(hours=24)),
        bus_id__order__notification_sent=False  # Проверяем по связанным заказам
    ).select_related('bus_id')
    
    for schedule in future_schedules:
        orders = Order.objects.filter(
            id_transport=schedule.bus_id,
            notification_sent=False
        ).select_related('id_client__user', 'id_transport')
        
        for order in orders:
            try:
                send_mail(
                    subject="Напоминание о вашем бронировании",
                    message=(
                        f"Уважаемый пользователь,\n\n"
                        f"Ваше бронирование автобуса {order.id_transport.bus_nickname} "
                        f"начнется {schedule.trip_start.strftime('%Y-%m-%d %H:%M')}.\n\n"
                        "Просим вас быть готовыми к поездке!\n"
                        "С уважением, Команда Маркетплейса"
                    ),
                    from_email="noreply@example.com",
                    recipient_list=[order.id_client.user.email],
                    fail_silently=False,
                )
                # Устанавливаем флаг, что уведомление отправлено
                order.notification_sent = True
                order.save()
            except Exception as e:
                print(f"Ошибка при отправке уведомления для заказа {order.id}: {e}")


