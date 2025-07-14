from django.test import TestCase
from places.models import Place
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

    def test_create_place(self):
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
        self.assertEqual(place.name, "Test Place")
        self.assertTrue(place.delivery)
        self.assertEqual(place.address, "Test Address")

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
