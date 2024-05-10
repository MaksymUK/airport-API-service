from rest_framework import serializers

from airport.models import (
    Airplane,
    AirplaneType,
    Airport,
    Route,
    Crew,
    Flight,
    Ticket,
    Order,
)


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name",)


class AirplaneSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type", "capacity")


class AirplaneDetailSerializer(AirplaneSerializer):
    airplane_type = AirplaneTypeSerializer()


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = serializers.StringRelatedField()


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city",)


class RouteSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(
        read_only=True, slug_field="name"
    )
    destination = serializers.SlugRelatedField(
        read_only=True, slug_field="name"
    )

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance",)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name",)


class FlightSerializer(serializers.ModelSerializer):

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time",)


class FlightDetailSerializer(FlightSerializer):
    route = RouteSerializer()
    airplane = AirplaneListSerializer()
    crew = serializers.StringRelatedField(many=True)

    class Meta:
        model = Flight
        fields = ("route", "airplane", "departure_time", "arrival_time", "crew",)


class FlightListSerializer(FlightSerializer):
    route = serializers.StringRelatedField()
    airplane_name = serializers.CharField(source="airplane.name", read_only=True)
    airplane_capacity = serializers.IntegerField(source="airplane.capacity", read_only=True)
    crew = serializers.StringRelatedField(many=True)

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane_name", "airplane_capacity", "departure_time", "arrival_time", "crew")


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "flight", "seat", "order",)


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, allow_empty=False, read_only=False)

    class Meta:
        model = Order
        fields = ("id", "created_at", "user", "tickets",)
