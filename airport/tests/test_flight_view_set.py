from django.contrib.auth import get_user_model
from django.db.models import F, Count
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from airport.models import Flight, Airport, Route, Airplane, AirplaneType, Crew, Ticket, Order
from airport.serializers import FlightListSerializer, FlightDetailSerializer

FLIGHT_URL = reverse("airport:flight-list")


class UnauthenticatedFlightViewSetApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_authentication_required(self):
        res = self.client.get(FLIGHT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedFlightViewSetApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@gmail.com", password="testuser123"
        )
        self.client.force_authenticate(self.user)

        airplane_type = AirplaneType.objects.create(name='Type A')
        self.airplane = Airplane.objects.create(
            name='Airplane 1',
            rows=10,
            seats_in_row=4,
            airplane_type=airplane_type
        )
        self.airport1 = Airport.objects.create(name='Airport 1', closest_big_city='City 1')
        self.airport2 = Airport.objects.create(name='Airport 2', closest_big_city='City 2')
        self.route = Route.objects.create(source=self.airport1, destination=self.airport2, distance=100)
        self.crew1 = Crew.objects.create(first_name='John', last_name='Doe')
        self.crew2 = Crew.objects.create(first_name='Jane', last_name='Doe')
        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time='2024-06-01T12:00:00Z',
            arrival_time='2024-06-01T14:00:00Z'
        )
        self.flight.crew.set([self.crew1, self.crew2])
        self.order = Order.objects.create(created_at='2024-06-01T10:00:00Z', user=self.user)
        Ticket.objects.create(flight=self.flight, seat=1, row=1, order=self.order)
        Ticket.objects.create(flight=self.flight, seat=2, row=1, order=self.order)

    def test_flights_list(self):
        res = self.client.get(FLIGHT_URL)

        flights = Flight.objects.annotate(
            remaining_seats=F("airplane__rows") * F("airplane__seats_in_row") - Count("tickets")
        )
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'], serializer.data)
        self.assertGreater(len(res.data['results']), 0)
        for flight_data in res.data['results']:
            self.assertIn('remaining_seats', flight_data)

    def test_retrieve_flight_detail(self):
        url = reverse("airport:flight-detail", args=[self.flight.id])
        res = self.client.get(url)

        flight = Flight.objects.get(id=self.flight.id)
        serializer = FlightDetailSerializer(flight)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_flight(self):
        payload = {
            'route': self.route.id,
            'airplane': self.airplane.id,
            'departure_time': '2024-06-02T12:00:00Z',
            'arrival_time': '2024-06-02T14:00:00Z',
            'crew': [self.crew1.id, self.crew2.id]
        }
        res = self.client.post(FLIGHT_URL, payload)
        # creation of flight permitted only for Admin user
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_flight(self):
        url = reverse("airport:flight-detail", args=[self.flight.id])
        payload = {
            'departure_time': '2024-06-01T13:00:00Z',
            'arrival_time': '2024-06-01T15:00:00Z'
        }
        res = self.client.patch(url, payload)
        # updating of flight permitted only for Admin user
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_flight_list_with_filters(self):
        res = self.client.get(FLIGHT_URL, {'route': f"{self.route.id}"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)

        res = self.client.get(FLIGHT_URL, {'departure_time': '2024-06-01'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)

        res = self.client.get(FLIGHT_URL, {'crew': 'John'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)


class AdminAuthenticatedFlightViewSetApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="testadmin@gmail.com", password="testadmin123")
        self.client.force_authenticate(self.user)

        airplane_type = AirplaneType.objects.create(name='Type B')
        self.airplane = Airplane.objects.create(
            name='Airplane 2',
            rows=10,
            seats_in_row=4,
            airplane_type=airplane_type
        )
        self.airport1 = Airport.objects.create(name='Airport 3', closest_big_city='City 3')
        self.airport2 = Airport.objects.create(name='Airport 4', closest_big_city='City 4')
        self.route = Route.objects.create(source=self.airport1, destination=self.airport2, distance=200)
        self.crew1 = Crew.objects.create(first_name='John', last_name='Smith')
        self.crew2 = Crew.objects.create(first_name='Jane', last_name='Smith')
        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time='2024-06-02T12:00:00Z',
            arrival_time='2024-06-02T14:00:00Z',
        )
        self.flight.crew.set([self.crew1, self.crew2])
        self.order = Order.objects.create(created_at='2024-06-02T10:00:00Z', user=self.user)
        Ticket.objects.create(flight=self.flight, seat=1, row=1, order=self.order)
        Ticket.objects.create(flight=self.flight, seat=2, row=1, order=self.order)

    def test_create_flight(self):
        payload = {
            'route': self.route.id,
            'airplane': self.airplane.id,
            'departure_time': '2024-06-03T12:00:00Z',
            'arrival_time': '2024-06-03T14:00:00Z',
            'crew': [self.crew1.id, self.crew2.id]
        }
        res = self.client.post(FLIGHT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Flight.objects.count(), 2)

    def test_delete_flight(self):
        url = reverse("airport:flight-detail", args=[self.flight.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_flight(self):
        url = reverse("airport:flight-detail", args=[self.flight.id])
        payload = {
            'departure_time': '2024-06-02T13:00:00Z',
            'arrival_time': '2024-06-02T15:00:00Z'
        }
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
