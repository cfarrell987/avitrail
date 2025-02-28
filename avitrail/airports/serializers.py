from rest_framework import serializers

from airports.models import Airport


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = "__all__"

    def create(self, validated_data):
        airport = Airport.objects.create(**validated_data)
        return airport
