from io import BytesIO

from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import F
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from airport.models import Airplane, AirplaneType
from airport.serializers import AirplaneSerializer, AirplaneImageSerializer, AirplaneListSerializer


AIRPLANE_URL = reverse("airport:airplane-list")


def sample_airplane_type(**params):
    defaults = {
        "name": "Type A",
    }
    defaults.update(params)

    return AirplaneType.objects.create(**defaults)


def sample_airplane(**params):
    if "airplane_type" not in params:
        params["airplane_type"] = sample_airplane_type()

    defaults = {
        "name": "Airplane 1",
        "rows": 10,
        "seats_in_row": 4,
    }
    defaults.update(params)

    return Airplane.objects.create(**defaults)


def detail_url(airplane_id) -> str:
    return reverse("airport:airplane-detail", args=[airplane_id])


def temporary_image():
    bts = BytesIO()
    img = Image.new("RGB", (100, 100))
    img.save(bts, 'jpeg')
    return SimpleUploadedFile("test.jpg", bts.getvalue())


class UnauthenticatedTestAirplaneViewSetApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_authentication_required(self):
        res = self.client.get(AIRPLANE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTestAirplaneViewSetApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@gmail.com", password="testuser123"
        )
        self.client.force_authenticate(self.user)

    def test_airplanes_list(self):
        sample_airplane()

        res = self.client.get(AIRPLANE_URL)

        airplanes = Airplane.objects.all()
        serializer = AirplaneListSerializer(airplanes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class AuthenticatedAdminTestAirplaneViewSetApiTest(TestCase):

        def setUp(self):
            self.client = APIClient()
            self.user = get_user_model().objects.create_superuser(
                email="testadmin@gmail.com", password="testadmin123"
            )
            self.client.force_authenticate(self.user)

        def test_create_airplane(self):
            payload = {
                'name': 'Airplane 2',
                'rows': 10,
                'seats_in_row': 4,
                'airplane_type': sample_airplane_type().id,
            }
            res = self.client.post(AIRPLANE_URL, payload)
            self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        def test_update_airplane(self):
            airplane = sample_airplane()
            url = detail_url(airplane.id)
            payload = {
                'rows': 12,
                'seats_in_row': 5,
            }
            res = self.client.patch(url, payload)
            self.assertEqual(res.status_code, status.HTTP_200_OK)

        def test_upload_image_to_airplane(self):
            airplane = sample_airplane()
            url = reverse("airport:airplane-upload-image", args=[airplane.id])
            with temporary_image() as img:
                res = self.client.post(url, {"image": img}, format="multipart")
            airplane.refresh_from_db()

            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertIn("image", res.data)
            self.assertTrue(airplane.image)
            self.assertTrue(airplane.image.url)

        def test_upload_image_bad_request(self):
            airplane = sample_airplane()
            url = reverse("airport:airplane-upload-image", args=[airplane.id])
            res = self.client.post(url, {"image": "not image"}, format="multipart")

            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        def test_image_url_is_shown_on_airplane_list(self):
            airplane = sample_airplane()
            url = reverse("airport:airplane-upload-image", args=[airplane.id])
            with temporary_image() as img:
                self.client.post(url, {"image": img}, format="multipart")
            res = self.client.get(AIRPLANE_URL)
            self.assertIn("image", res.data[0])
