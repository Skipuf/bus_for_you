from django.utils.timezone import now

from database.models import *
from rest_framework import serializers


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ['id_from', 'id_to']


class TransportSerializer(serializers.ModelSerializer):
    route = RouteSerializer()  # Чтобы отображать информацию по маршруту
    
    class Meta:
        model = Transport
        fields = [
            'id', 'brand', 'model', 'year_issued', 'n_deck', 'n_seats',
            'photo', 'luggage', 'wifi', 'tv', 'toilet', 'route'
        ]  # потом нужно добавить 'rating'


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['trip_start', 'trip_end']


class OrderSerializer(serializers.ModelSerializer):
    # Чтобы отображать строковые представления автобуса и маршрута
    transport = TransportSerializer(read_only=True)
    route = serializers.StringRelatedField()
    
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['id_client', 'status', 'create_time']

    def validate(self, data):
        start_date = data['time_range'].lower
        end_date = data['time_range'].upper

        if start_date >= end_date:
            raise serializers.ValidationError("End date must be after start date.")

        if start_date < now():
            raise serializers.ValidationError("Start date cannot be in the past.")

        return data
    