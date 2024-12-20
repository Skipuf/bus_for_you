from rest_framework import serializers
from database.models import Mailing


class MailingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mailing
        fields = ['id', 'subject', 'body', 'send_time', 'is_sent', 'task_id', 'failed_recipients']
        read_only_fields = ['is_sent', 'task_id', 'failed_recipients']
