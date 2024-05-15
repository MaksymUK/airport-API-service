from django.db.models import Count, F, Q
from django.utils.dateparse import parse_date
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
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
from .permissions import IsAdminOrIfAuthenticatedReadOnly
from .serializers import (
    AirplaneTypeSerializer,
    AirplaneSerializer,
    AirplaneImageSerializer,
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
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class AirplaneViewSet(
    viewsets.ModelViewSet
):
    queryset = Airplane.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AirplaneDetailSerializer
        if self.action == 'list':
            return AirplaneListSerializer
        if self.action == 'upload_image':
            return AirplaneImageSerializer

        return AirplaneSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            return queryset.select_related()

        return queryset

    @action(
        methods=("POST",),
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        item = self.get_object()
        serializer = self.get_serializer(item, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AirportViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class RouteViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Route.objects.all().select_related()
    serializer_class = RouteSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class CrewViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class FlightViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Flight.objects.all().select_related()
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

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
            parsed_date = parse_date(departure_time)
            if parsed_date:
                queryset = queryset.filter(departure_time__date=parsed_date)

        if crew:
            queryset = queryset.filter(Q(crew__last_name__icontains=crew) | Q(crew__first_name__icontains=crew))

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
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


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
