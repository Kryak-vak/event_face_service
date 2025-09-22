from rest_framework import serializers

from .models import Event, EventRegistration


class EventSerializer(serializers.ModelSerializer):
    venue_name = serializers.CharField(source="venue.name", read_only=True)

    class Meta:
        model = Event
        fields = "__all__"


class EventRegistrationSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=128)
    email = serializers.EmailField()