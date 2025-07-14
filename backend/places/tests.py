from django.test import TestCase
from places.models import Place


class PlaceModelTest(TestCase):
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
