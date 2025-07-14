from django.test import TestCase
from places.models import Place
from places_menu.models import Menu
from shwarma.models import Shwarma
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io
from django.core.exceptions import ValidationError
from decimal import Decimal


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
        self.client.force_login(self.user)

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
            "district": "Unknown",
            "address": "Test Address",
            "delivery": True,
            "longitude": "30.5234",
            "description": "Test Description",
            "main_image": uploaded_image,
        }
        response = self.client.post(
            "/api/places/create-place/", data, format="multipart"
        )
        print(response.data)
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
        from reviews.models import Review

        Review.objects.create(
            place=self.place, author=self.user, score=8.0, comment="Good"
        )
        Review.objects.create(
            place=self.place, author=self.user, score=6.0, comment="OK"
        )

        avg_rating = self.place.calculate_average_rating()
        self.assertEqual(avg_rating, Decimal("7.0"))

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
