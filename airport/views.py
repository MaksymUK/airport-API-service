from django.db.models import Count, F
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
    AirplaneDetailSerializer,
    AirplaneListSerializer,
    AirportSerializer,
    RouteSerializer,
    CrewSerializer,
    FlightSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
    OrderSerializer,
    OrderListSerializer,
)


class AirplaneTypeViewSet(
    viewsets.ModelViewSet
):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(
    viewsets.ModelViewSet
):
    queryset = Airplane.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AirplaneDetailSerializer
        if self.action == 'list':
            return AirplaneListSerializer

        return AirplaneSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            return queryset.select_related()

        return queryset


class AirportViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer


class RouteViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Route.objects.all().select_related()
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
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Flight.objects.all().select_related()

    @staticmethod
    def _params_to_ints(query_string):
        return [int(str_id) for str_id in query_string.split(",")]

    def get_serializer_class(self):
        if self.action == 'list':
            return FlightListSerializer
        if self.action == 'retrieve':
            return FlightDetailSerializer

        return FlightSerializer

    def get_queryset(self):
        queryset = self.queryset
        route = self.request.query_params.get("route")
        departure_time = self.request.query_params.get("departure_time")
        crew = self.request.query_params.get("crew")

        if route:
            route = self._params_to_ints(route)
            queryset = queryset.filter(route__id__in=route)

        if departure_time:
            queryset = queryset.filter(departure_time=departure_time)

        if crew:
            queryset = queryset.filter(crew__last_name__icontains=crew)

        if self.action == "list":
            queryset = queryset.prefetch_related("airplane").annotate(
                remaining_seats=F("airplane__rows") * F("airplane__seats_in_row") - Count("tickets"),
            )

        return queryset.distinct()


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    # def get_queryset(self):
    #     return self.queryset.filter(user=self.request.user)
    #
    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)
    #
    # def get_serializer_class(self):
    #     serializer = self.serializer_class
    #     if self.action == "list":
    #         serializer = OrderListSerializer
    #     return serializer
