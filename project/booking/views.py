from datetime import datetime

from django.shortcuts import render, redirect
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status, filters
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from project.utils import StandardResponseMixin
from .serializers import *
from database.models import *


class TransportViewSet(StandardResponseMixin, viewsets.ModelViewSet):
    queryset = Transport.objects.all()
    serializer_class = TransportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['n_seats', 'luggage', 'wifi', 'tv', 'toilet']
    ordering_fields = ['n_seats']  # Потом добавить 'rating'

    @swagger_auto_schema(
        tags=["[booking] автобус"],
        operation_description="(только для тестов, может не работать) Получить список автобусов.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["[booking] автобус"],
        operation_description="(только для тестов, может не работать) Создать новый автобус.",
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["[booking] автобус"],
        operation_description="(только для тестов, может не работать) Получить автобус по ID.",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["[booking] автобус"],
        operation_description="(только для тестов, может не работать) Обновить существующий автобус.",
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["[booking] автобус"],
        operation_description="(только для тестов, может не работать) Обновить существующий автобус.",
    )
    def update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["[booking] автобус"],
        operation_description="(только для тестов, может не работать) Удалить существующий автобус.",
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["[booking] бронь (в разработке)"],
        operation_description="Проверка доступности автобуса на заданный период.",
        manual_parameters=[
            openapi.Parameter(
                'start_date',
                openapi.IN_QUERY,
                description="Дата начала периода",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                'end_date',
                openapi.IN_QUERY,
                description="Дата окончания периода",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Успешный ответ.",
                examples={"application/json": {"is_available": True}}
            ),
            400: openapi.Response(
                description="Некорректные параметры запроса.",
                examples={"application/json": {"error": "Start and end dates are required"}}
            ),
            404: openapi.Response(
                description="Транспорт не найден.",
                examples={"application/json": {"error": "Transport not found"}}
            ),
        }
    )
    @action(detail=True, methods=['get'], url_path='availability')
    def check_availability(self, request, pk=None):
        try:
            transport = self.get_object()
        except Transport.DoesNotExist:
            return Response({"error": "Transport not found"}, status=status.HTTP_404_NOT_FOUND)

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            return Response({"error": "Start and end dates are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            start_date = datetime.fromisoformat(start_date)
            end_date = datetime.fromisoformat(end_date)
        except ValueError:
            return Response({"error": "Invalid date format."}, status=status.HTTP_400_BAD_REQUEST)

        if start_date < now():
            return Response({"error": "Start date cannot be in the past."}, status=status.HTTP_400_BAD_REQUEST)

        # Проверка доступности
        is_available = not transport.schedule_set.filter(
            trip_start__lt=end_date,
            trip_end__gt=start_date
        ).exists()

        return Response({"is_available": is_available}, status=status.HTTP_200_OK)


class ScheduleApiView(APIView):
    pass


class BusSearchApiView(StandardResponseMixin, ListAPIView):
    serializer_class = TransportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['n_seats', 'order__price', 'id_route__id_from', 'id_route__id_to', 'luggage', 'wifi', 'tv',
                        'toilet']
    ordering_fields = ['price', 'n_seats']  # Потом добавить 'rating'

    def get_queryset(self):
        queryset = Transport.objects.all().select_related('route')

        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            try:
                start_date = datetime.fromisoformat(start_date)
                end_date = datetime.fromisoformat(end_date)
            except ValueError:
                return queryset.none()

            unavailable_transports = Schedule.objects.filter(
                trip_start__lt=end_date,
                trip_end__gt=start_date
            ).values_list('bus_id', flat=True)
            queryset = queryset.exclude(id__in=unavailable_transports)

        return queryset

    @swagger_auto_schema(
        tags=["[booking] бронь (в разработке)"],
        operation_description="Поиск автобуса с фильтрацией и сортировкой.",
        manual_parameters=[
            openapi.Parameter(
                'start_date',
                openapi.IN_QUERY,
                description="Дата начала поездки в формате YYYY-MM-DD",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                'end_date',
                openapi.IN_QUERY,
                description="Дата окончания поездки в формате YYYY-MM-DD",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class BookingCreateApiView(StandardResponseMixin, CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if not hasattr(self.request.user, 'client'):
            raise ValueError("User must have an associated client.")
        serializer.save(id_client=self.request.user.client)

    @swagger_auto_schema(
        tags=["[booking] бронь (в разработке)"],
        operation_description="Создание брони.",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class BookingListClientApiView(StandardResponseMixin, ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects.filter(id_client=self.request.user.client)
            .select_related('id_transport', 'id_route', 'id_carrier')  # Оптимизация связанных объектов
            .prefetch_related('id_transport__schedule')  # Предварительная выборка расписаний
        )

    @swagger_auto_schema(
        tags=["[booking] бронь (в разработке)"],
        operation_description="Список бронирований клиента.",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class BookingListCarrierApiView(StandardResponseMixin, ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects.filter(id_carrier=self.request.user.carrier)
            .select_related('id_transport', 'id_route', 'id_client')
            .prefetch_related('id_transport__schedule')
        )

    @swagger_auto_schema(
        tags=["[booking] бронь (в разработке)"],
        operation_description="Список бронирований транспортной компании.",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class BookingDetailApiView(StandardResponseMixin, RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["[booking] бронь (в разработке)"],
        operation_description="Получить бронь по айди.",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class BookingUpdateApiView(StandardResponseMixin, UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["[booking] бронь (в разработке)"],
        operation_description="Обновить бронь по айди.",
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["[booking] бронь (в разработке)"],
        operation_description="Обновить бронь по айди.",
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class BookingDeleteApiView(StandardResponseMixin, DestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["[booking] бронь (в разработке)"],
        operation_description="Удалить бронь по айди.",
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


def redirect_swagger(*args):
    return redirect("swagger-ui")
