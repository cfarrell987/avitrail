from rest_framework import serializers

from airlines.models import Airline


class AirlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airline
        fields = "__all__"

    def create(self, validated_data):
        airline = Airline.objects.create(**validated_data)
        return airline
