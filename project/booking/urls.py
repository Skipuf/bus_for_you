from django.urls import path
from rest_framework.routers import DefaultRouter
from booking.views import (
    TransportViewSet,
    BusSearchApiView,
    BookingCreateApiView,
    BookingListClientApiView,
    BookingListCarrierApiView,
    BookingDetailApiView,
    BookingUpdateApiView,
    BookingDeleteApiView,
)

router = DefaultRouter()
router.register(r'buses', TransportViewSet, basename='buses')

urlpatterns = [
    path('search/', BusSearchApiView.as_view(), name='bus-search'),
    path('', BookingCreateApiView.as_view(), name='booking-create'),
    path('user/', BookingListClientApiView.as_view(), name='booking-list-client'),
    # Сделано bookings/carrier/ вместо bookings/company/ для ясности
    path('carrier/', BookingListCarrierApiView.as_view(), name='booking-list-carrier'),
    path('<int:pk>/', BookingDetailApiView.as_view(), name='booking-detail'),
    path('<int:pk>/update/', BookingUpdateApiView.as_view(), name='booking-update'),
    path('<int:pk>/delete/', BookingDeleteApiView.as_view(), name='booking-delete'),
]

urlpatterns += router.urls