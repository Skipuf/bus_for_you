from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils.timezone import now
from celery import current_app
from database.models import Mailing, Subscription
from project.utils import StandardResponseMixin
from .serializers import MailingSerializer
from .tasks import send_notification


class MailingListView(StandardResponseMixin, generics.ListAPIView):
    queryset = Mailing.objects.all().order_by('send_time')
    serializer_class = MailingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        tags=["[notification] уведомления (в разработке)"],
        operation_description="Получить список уведомлений.",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class MailingCreateView(StandardResponseMixin, generics.CreateAPIView):
    queryset = Mailing.objects.all()
    serializer_class = MailingSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        mailing = serializer.save()
        if mailing.send_time and mailing.send_time > now():
            task = send_notification.apply_async((mailing.id,), eta=mailing.send_time)
            mailing.task_id = task.id
            mailing.save()

    @swagger_auto_schema(
        tags=["[notification] уведомления (в разработке)"],
        operation_description="Получить список уведомлений.",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class MailingUpdateView(StandardResponseMixin, generics.UpdateAPIView):
    queryset = Mailing.objects.all()
    serializer_class = MailingSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_update(self, serializer):
        mailing = serializer.save()
        if not mailing.is_sent and mailing.send_time > now():
            if mailing.task_id:
                current_app.control.revoke(mailing.task_id, terminate=True)  # Отзываем задачу
            task = send_notification.apply_async((mailing.id,), eta=mailing.send_time)
            mailing.task_id = task.id
            mailing.save()

    @swagger_auto_schema(
        tags=["[notification] уведомления (в разработке)"],
        operation_description="Обновить уведомление по айди.",
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["[notification] уведомления (в разработке)"],
        operation_description="Обновить уведомление по айди.",
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class MailingDeleteView(StandardResponseMixin, generics.DestroyAPIView):
    queryset = Mailing.objects.all()
    serializer_class = MailingSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_destroy(self, instance):
        if instance.task_id:
            current_app.control.revoke(instance.task_id, terminate=True)
        super().perform_destroy(instance)

    @swagger_auto_schema(
        tags=["[notification] уведомления (в разработке)"],
        operation_description="Удалить уведомление по айди.",
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


@swagger_auto_schema(
    method='post',
    tags=["[notification] уведомления (в разработке)"],
    operation_description="Подписаться на рассылку.",
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def subscribe_to_mailing(request, mailing_id):
    subscription, created = Subscription.objects.get_or_create(
        user=request.user,
        mailing_id=mailing_id,
        defaults={'subscribed': True}
    )
    if not created:
        subscription.subscribed = True
        subscription.save()
    return Response({"message": "Subscribed successfully"})


@swagger_auto_schema(
    method='post',
    tags=["[notification] уведомления (в разработке)"],
    operation_description="Отписаться от рассылки.",
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def unsubscribe_from_mailing(request, mailing_id):
    try:
        subscription = Subscription.objects.get(user=request.user, mailing_id=mailing_id)
        subscription.subscribed = False
        subscription.save()
    except Subscription.DoesNotExist:
        pass
    return Response({"message": "Unsubscribed successfully"})
