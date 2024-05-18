import pathlib
import uuid

from django.db import models
from django.conf import settings
from django.db.models import UniqueConstraint
from django.utils.text import slugify


class AirplaneType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


def create_custom_path(instance: "Airplane", filename: str) -> pathlib.Path:
    filename = (
        f"{slugify(instance.name)}-{uuid.uuid4()}"
        + pathlib.Path(filename).suffix
    )
    return pathlib.Path("uploads/airplanes/") / pathlib.Path(filename)


class Airplane(models.Model):
    name = models.CharField(max_length=255, unique=True)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to=create_custom_path, null=True, blank=True
    )

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name


class Airport(models.Model):
    name = models.CharField(max_length=255, unique=True)
    closest_big_city = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} ({self.closest_big_city})"


class Route(models.Model):
    source = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='departure_airport')
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='arrival_airport')
    distance = models.IntegerField()

    def __str__(self):
        return f"{self.source} - {self.destination}, {self.distance} km"


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE, related_name='flights')
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name='flights')

    def __str__(self):
        return f"{self.airplane} - {self.route}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.created_at.strftime("%Y-%m-%d %H:%M:%S")

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tickets')

    class Meta:
        unique_together = ("seat", "flight")
        ordering = ("seat",)

    def __str__(self):
        return f"{self.flight} - {self.seat}"

    @staticmethod
    def validate_ticket(row, seat, airplane, error_to_raise):
        if not (1 <= row <= airplane.rows):
            raise error_to_raise({"row": f"row {row} is out of range"})
        if not (1 <= seat <= airplane.seats_in_row):
            raise error_to_raise({"seat": f"seat {seat} is out of range"})
        if Ticket.objects.filter(row=row, seat=seat, flight__airplane=airplane).exists():
            raise error_to_raise({"seat": f"seat {seat} is already taken"})

    def clean(self):
        if self.flight.airplane.capacity < Ticket.objects.filter(flight=self.flight).count():
            raise ValueError("No available seats")

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None
    ):
        self.full_clean()
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields
        )
