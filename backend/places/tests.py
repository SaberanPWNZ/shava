import io
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image
from rest_framework.test import APIClient

from places.models import Place, PlaceRating
from places_menu.models import Menu
from shwarma.models import Shwarma


class PlaceModelTest(TestCase):
    def setUp(self):
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
        self.shwarma = Shwarma.objects.create(
            name="Test Shwarma",
            place=self.place,
            description="Test",
            size="M",
            price=100,
            main_image="test.jpg",
        )
        self.menu = Menu.objects.create(
            name="Test Menu",
            place=self.place,
            item=self.shwarma,
        )
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com", password="testpass123", username="testuser"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_place(self):
        image = Image.new("RGB", (1, 1), color="red")
        image_file = io.BytesIO()
        image.save(image_file, format="PNG")
        image_file.seek(0)

        uploaded_image = SimpleUploadedFile(
            "test.png", image_file.getvalue(), content_type="image/png"
        )

        data = {
            "name": "Test Place API",
            "city": "Kyiv",
            "address": "Test Address",
            "delivery": True,
            "latitude": "50.4501",
            "longitude": "30.5234",
            "description": "Test Description",
            "main_image": uploaded_image,
        }
        response = self.client.post(
            "/api/places/create-place/", data, format="multipart"
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Place.objects.filter(name="Test Place API").exists())

    def test_update_place(self):
        place = Place.objects.create(
            name="Test Place",
            district="Unknown",
            address="Test Address",
            delivery=True,
            latitude=50.4501,
            longitude=30.5234,
            description="Test Description",
            main_image="test.jpg",
        )
        place.name = "Updated Place"
        place.save()
        self.assertEqual(place.name, "Updated Place")

    def test_delete_place(self):
        place = Place.objects.create(
            name="Test Place",
            district="Unknown",
            address="Test Address",
            delivery=True,
            latitude=50.4501,
            longitude=30.5234,
            description="Test Description",
            main_image="test.jpg",
        )
        place_id = place.id
        place.delete()
        self.assertFalse(Place.objects.filter(id=place_id).exists())

    def test_str_method(self):
        place = Place.objects.create(
            name="Test Place",
            district="Unknown",
            address="Test Address",
            delivery=True,
            latitude=50.4501,
            longitude=30.5234,
            description="Test Description",
            main_image="test.jpg",
        )
        self.assertEqual(str(place), "Test Place")

    def test_rating_validation(self):
        place = Place.objects.create(
            name="Test Place",
            district="Unknown",
            address="Test Address",
            main_image="test.jpg",
            rating=5.5,
        )
        self.assertEqual(place.rating, Decimal("5.5"))

        place.rating = 15.0
        with self.assertRaises(ValidationError):
            place.full_clean()

    def test_google_maps_url_method(self):
        place = self.place
        expected_url = f"https://www.google.com/maps/search/?api=1&query={place.latitude},{place.longitude}"
        self.assertEqual(place.google_maps_url(), expected_url)

        place_no_coords = Place.objects.create(
            name="No Coords Place",
            district="Unknown",
            address="Test Address",
            main_image="test.jpg",
        )
        self.assertIsNone(place_no_coords.google_maps_url())

    def test_calculate_average_rating(self):
        other_user = get_user_model().objects.create_user(
            email="rater2@example.com", password="testpass123", username="rater2"
        )
        PlaceRating.objects.create(place=self.place, user=self.user, rating=8.0)
        PlaceRating.objects.create(place=self.place, user=other_user, rating=6.0)

        avg_rating = self.place.calculate_average_rating()
        self.assertEqual(avg_rating, Decimal("7.0"))

    def test_recalculate_rating_from_reviews(self):
        from reviews.models import Review

        Review.objects.create(
            place=self.place,
            author=self.user,
            score=8.0,
            comment="Good",
            is_moderated=True,
        )
        # Unmoderated reviews must not affect the rating.
        Review.objects.create(
            place=self.place, author=self.user, score=2.0, comment="Spam"
        )

        self.place.recalculate_rating_from_reviews()
        self.place.refresh_from_db()
        self.assertEqual(self.place.rating, Decimal("8.0"))

    def test_required_fields(self):
        with self.assertRaises(ValidationError):
            place = Place(district="Unknown")
            place.full_clean()

    def test_district_choices(self):
        place = Place.objects.create(
            name="Test Place",
            district="Dnipro",
            address="Test Address",
            main_image="test.jpg",
        )
        self.assertEqual(place.district, "Dnipro")

    def test_default_values(self):
        place = Place.objects.create(
            name="Test Place",
            district="Unknown",
            address="Test Address",
            main_image="test.jpg",
        )
        self.assertFalse(place.delivery)
        self.assertFalse(place.is_featured)
        self.assertEqual(place.rating, Decimal("0.0"))
