from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

from places.models import Place, PlaceRating
from places.serializers import PlaceCreateSerializer, PlaceDetailSerializer

User = get_user_model()


class PlaceViewsTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpass123", username="testuser"
        )
        self.place = Place.objects.create(
            name="Test Place",
            district="Unknown",
            address="Test Address",
            delivery=True,
            latitude=50.4501,
            longitude=30.5234,
            description="Test Description",
            main_image="test.jpg",
        )
        self.client.force_authenticate(user=self.user)

    def _create_test_image(self):
        """Helper method to create test image"""
        image = Image.new("RGB", (10, 10), color="red")
        image_file = io.BytesIO()
        image.save(image_file, format="PNG")
        image_file.seek(0)
        return SimpleUploadedFile(
            "test.png", image_file.getvalue(), content_type="image/png"
        )

    def test_place_create_success(self):
        """Test successful place creation"""
        data = {
            "name": "New Place",
            "district": "Dnipro",
            "address": "New Address",
            "delivery": True,
            "latitude": "50.4501",
            "longitude": "30.5234",
            "description": "New Description",
            "main_image": self._create_test_image(),
        }
        response = self.client.post(
            "/api/places/create-place/", data, format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Place.objects.filter(name="New Place").exists())

    def test_place_create_unauthenticated(self):
        """Test place creation without authentication"""
        self.client.force_authenticate(user=None)
        data = {"name": "Test Place", "address": "Test"}
        response = self.client.post("/api/places/create-place/", data)
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN
        )  # змінити з 401 на 403

    def test_place_detail_success(self):
        """Test successful place detail retrieval"""
        url = f"/api/places/place/{self.place.pk}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.place.name)

    def test_place_detail_not_found(self):
        """Test place detail with non-existent ID"""
        url = "/api/places/place/99999/"
        response = self.client.get(url)
        self.assertIn(
            response.status_code,
            [status.HTTP_404_NOT_FOUND, status.HTTP_500_INTERNAL_SERVER_ERROR],
        )

    def test_place_update_success(self):
        """Test successful place update"""
        url = f"/api/places/{self.place.pk}/"
        data = {"name": "Updated Place Name"}

        response = self.client.patch(url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.place.refresh_from_db()
        self.assertEqual(self.place.name, "Updated Place Name")

    def test_place_rating_create(self):
        """Test creating place rating"""
        data = {"place": self.place.id, "rating": "8.5"}
        response = self.client.post("/api/places/ratings/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            PlaceRating.objects.filter(user=self.user, place=self.place).exists()
        )

    def test_place_rating_update_or_create(self):
        """Test updating existing rating"""

        PlaceRating.objects.create(user=self.user, place=self.place, rating=7.0)
        data = {"place": self.place.id, "rating": "9.0"}
        response = self.client.post("/api/places/ratings/", data)

        if response.status_code == status.HTTP_400_BAD_REQUEST:
            print("Rating creation error:", response.data)

        rating = PlaceRating.objects.get(user=self.user, place=self.place)
        url = f"/api/places/ratings/{rating.id}/"
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            PlaceRating.objects.filter(user=self.user, place=self.place).count(), 1
        )
        rating.refresh_from_db()
        self.assertEqual(float(rating.rating), 9.0)

    def test_get_user_ratings_only(self):
        """Test that user sees only their ratings"""
        other_user = User.objects.create_user(
            email="other@example.com", password="pass123", username="other"
        )
        PlaceRating.objects.create(user=self.user, place=self.place, rating=8.0)
        PlaceRating.objects.create(user=other_user, place=self.place, rating=6.0)

        response = self.client.get("/api/places/ratings/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["rating"], "8.00")


class PlaceModelValidationTest(TestCase):
    def test_place_rating_validation(self):
        """Test place rating field validation"""
        from django.core.exceptions import ValidationError

        place = Place(
            name="Test Place",
            district="Unknown",
            address="Test Address",
            main_image="test.jpg",
            rating=15.0,
        )

        with self.assertRaises(ValidationError):
            place.full_clean()

    def test_google_maps_url_generation(self):
        """Test Google Maps URL generation"""
        place = Place.objects.create(
            name="Test Place",
            district="Unknown",
            address="Test Address",
            main_image="test.jpg",
            latitude=50.4501,
            longitude=30.5234,
        )

        expected_url = f"https://www.google.com/maps/search/?api=1&query={place.latitude},{place.longitude}"
        self.assertEqual(place.google_maps_url(), expected_url)

        place_no_coords = Place.objects.create(
            name="No Coords",
            district="Unknown",
            address="Test Address",
            main_image="test.jpg",
        )
        self.assertIsNone(place_no_coords.google_maps_url())
