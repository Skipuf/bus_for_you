from django.urls import path
from notification.views import MailingListView, MailingCreateView, MailingUpdateView, MailingDeleteView, \
    subscribe_to_mailing, unsubscribe_from_mailing

urlpatterns = [
    path('', MailingListView.as_view(), name='mailing-list'),
    path('create/', MailingCreateView.as_view(), name='mailing-create'),
    path('<int:pk>/update/', MailingUpdateView.as_view(), name='mailing-update'),
    path('<int:pk>/delete/', MailingDeleteView.as_view(), name='mailing-delete'),
    path('subscribe/', subscribe_to_mailing, name='mailing-subscribe'),
    path('unsubscribe/', unsubscribe_from_mailing, name='mailing-unsubscribe'),
]
