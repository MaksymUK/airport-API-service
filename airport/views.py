
from rest_framework import viewsets, mixins, status
from rest_framework.viewsets import GenericViewSet
from rest_framework import generics
from .models import (
    Airplane,
    AirplaneType,
    Airport,
    Route,
    Crew,
    Flight,
    Order,
)
from .serializers import (
    AirplaneTypeSerializer,
    AirplaneSerializer,
    AirportSerializer,
    RouteSerializer,
    CrewSerializer,
    FlightSerializer,
    OrderSerializer,
)


class AirplaneTypeViewSet(
    viewsets.ModelViewSet
):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer


class AirportViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer


class RouteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer


class CrewViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class FlightViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

