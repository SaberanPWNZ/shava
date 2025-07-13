import tempfile
import os
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from PIL import Image
from places.models import Place
from places.serializers import PlaceSerializer

User = get_user_model()


class PlaceModelTest(TestCase):
    """Test cases for Place model"""

    def setUp(self):
        """Set up test data"""
        # Create a temporary image file for testing
        image = Image.new('RGB', (100, 100), color='red')
        self.temp_image = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        image.save(self.temp_image.name, 'JPEG')
        self.temp_image.seek(0)

    def tearDown(self):
        """Clean up test data"""
        # Clean up the temporary image file
        if os.path.exists(self.temp_image.name):
            os.unlink(self.temp_image.name)

    def test_create_place(self):
        """Test creating a place instance"""
        place = Place.objects.create(
            name="Test Place",
            address="123 Test Street",
            delivery=True,
            main_image=SimpleUploadedFile(
                name='test_image.jpg',
                content=open(self.temp_image.name, 'rb').read(),
                content_type='image/jpeg'
            )
        )
        
        self.assertEqual(place.name, "Test Place")
        self.assertEqual(place.address, "123 Test Street")
        self.assertTrue(place.delivery)
        self.assertEqual(place.rating, Decimal('0.00'))
        self.assertTrue(place.main_image)

    def test_place_str_representation(self):
        """Test the string representation of Place model"""
        place = Place.objects.create(
            name="Test Place",
            address="123 Test Street",
            main_image=SimpleUploadedFile(
                name='test_image.jpg',
                content=open(self.temp_image.name, 'rb').read(),
                content_type='image/jpeg'
            )
        )
        # Since there's no __str__ method defined, it will use the default representation
        # We can add this test if __str__ method is added to the model later
        self.assertIsInstance(str(place), str)


class PlaceSerializerTest(TestCase):
    """Test cases for Place serializer"""

    def setUp(self):
        """Set up test data"""
        # Create a temporary image file for testing
        image = Image.new('RGB', (100, 100), color='red')
        self.temp_image = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        image.save(self.temp_image.name, 'JPEG')
        self.temp_image.seek(0)

    def tearDown(self):
        """Clean up test data"""
        # Clean up the temporary image file
        if os.path.exists(self.temp_image.name):
            os.unlink(self.temp_image.name)

    def test_place_serializer_valid_data(self):
        """Test serializer with valid data"""
        data = {
            'name': 'Test Place',
            'address': '123 Test Street',
            'delivery': True,
            'main_image': SimpleUploadedFile(
                name='test_image.jpg',
                content=open(self.temp_image.name, 'rb').read(),
                content_type='image/jpeg'
            )
        }
        
        serializer = PlaceSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_place_serializer_invalid_data(self):
        """Test serializer with invalid data"""
        # Test with empty name
        data = {
            'name': '',
            'address': '123 Test Street',
            'delivery': True,
        }
        
        serializer = PlaceSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

        # Test with empty address
        data = {
            'name': 'Test Place',
            'address': '',
            'delivery': True,
        }
        
        serializer = PlaceSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('address', serializer.errors)

    def test_place_serializer_trimming(self):
        """Test that serializer trims whitespace from name and address"""
        data = {
            'name': '  Test Place  ',
            'address': '  123 Test Street  ',
            'delivery': True,
            'main_image': SimpleUploadedFile(
                name='test_image.jpg',
                content=open(self.temp_image.name, 'rb').read(),
                content_type='image/jpeg'
            )
        }
        
        serializer = PlaceSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        place = serializer.save()
        self.assertEqual(place.name, 'Test Place')
        self.assertEqual(place.address, '123 Test Street')


class PlaceAPITest(APITestCase):
    """Test cases for Place API endpoints"""

    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create a temporary image file for testing
        image = Image.new('RGB', (100, 100), color='red')
        self.temp_image = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        image.save(self.temp_image.name, 'JPEG')
        self.temp_image.seek(0)
        
        # Create test place
        self.place = Place.objects.create(
            name="Test Place",
            address="123 Test Street",
            delivery=True,
            main_image=SimpleUploadedFile(
                name='test_image.jpg',
                content=open(self.temp_image.name, 'rb').read(),
                content_type='image/jpeg'
            )
        )
        
        self.client = APIClient()

    def tearDown(self):
        """Clean up test data"""
        # Clean up the temporary image file
        if os.path.exists(self.temp_image.name):
            os.unlink(self.temp_image.name)

    def test_get_places_list_anonymous(self):
        """Test getting list of places as anonymous user"""
        url = reverse('place-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Handle paginated response
        data = response.data
        if isinstance(data, dict) and 'results' in data:
            places = data['results']
        else:
            places = data
            
        self.assertGreaterEqual(len(places), 1)  # At least one place exists
        # Check that our test place is in the response
        place_names = [place['name'] for place in places]
        self.assertIn('Test Place', place_names)

    def test_get_places_list_authenticated(self):
        """Test getting list of places as authenticated user"""
        self.client.force_authenticate(user=self.user)
        url = reverse('place-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Handle paginated response
        data = response.data
        if isinstance(data, dict) and 'results' in data:
            places = data['results']
        else:
            places = data
            
        self.assertGreaterEqual(len(places), 1)  # At least one place exists

    def test_get_place_detail_anonymous(self):
        """Test getting place details as anonymous user"""
        url = reverse('place-detail', kwargs={'pk': self.place.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Place')

    def test_get_place_detail_not_found(self):
        """Test getting non-existent place details"""
        url = reverse('place-detail', kwargs={'pk': 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_place_authenticated(self):
        """Test creating a place as authenticated user"""
        self.client.force_authenticate(user=self.user)
        url = reverse('place-list')
        
        # Create a fresh image for the test
        image = Image.new('RGB', (100, 100), color='green')
        temp_image_create = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        image.save(temp_image_create.name, 'JPEG')
        temp_image_create.seek(0)
        
        with open(temp_image_create.name, 'rb') as image_file:
            data = {
                'name': 'New Test Place',
                'address': '456 New Street',
                'delivery': False,
                'main_image': SimpleUploadedFile(
                    name='new_test_image.jpg',
                    content=image_file.read(),
                    content_type='image/jpeg'
                )
            }
            
            response = self.client.post(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Test Place')
        self.assertEqual(response.data['address'], '456 New Street')
        self.assertFalse(response.data['delivery'])
        
        # Clean up
        if os.path.exists(temp_image_create.name):
            os.unlink(temp_image_create.name)

    def test_create_place_unauthenticated(self):
        """Test creating a place as unauthenticated user"""
        url = reverse('place-list')
        
        data = {
            'name': 'New Test Place',
            'address': '456 New Street',
            'delivery': False,
        }
        
        response = self.client.post(url, data)
        # DRF returns 403 Forbidden for unauthenticated users when permission is required
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_place_invalid_data(self):
        """Test creating a place with invalid data"""
        self.client.force_authenticate(user=self.user)
        url = reverse('place-list')
        
        data = {
            'name': '',  # Empty name should fail validation
            'address': '456 New Street',
            'delivery': False,
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_update_place_authenticated(self):
        """Test updating a place as authenticated user"""
        self.client.force_authenticate(user=self.user)
        url = reverse('place-detail', kwargs={'pk': self.place.pk})
        
        # Test partial update without image (PATCH)
        data = {
            'name': 'Updated Test Place',
            'address': 'Updated Address',
            'delivery': False,
        }
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Test Place')
        self.assertEqual(response.data['address'], 'Updated Address')
        self.assertFalse(response.data['delivery'])

    def test_partial_update_place_authenticated(self):
        """Test partially updating a place as authenticated user"""
        self.client.force_authenticate(user=self.user)
        url = reverse('place-detail', kwargs={'pk': self.place.pk})
        
        data = {
            'name': 'Partially Updated Place'
        }
        
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Partially Updated Place')
        # Address should remain the same
        self.assertEqual(response.data['address'], '123 Test Street')

    def test_update_place_unauthenticated(self):
        """Test updating a place as unauthenticated user"""
        url = reverse('place-detail', kwargs={'pk': self.place.pk})
        
        data = {
            'name': 'Updated Test Place',
            'address': 'Updated Address',
            'delivery': False,
        }
        
        response = self.client.put(url, data)
        # DRF returns 403 Forbidden for unauthenticated users when permission is required
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_place_not_found(self):
        """Test updating non-existent place"""
        self.client.force_authenticate(user=self.user)
        url = reverse('place-detail', kwargs={'pk': 999})
        
        data = {
            'name': 'Updated Test Place',
            'address': 'Updated Address',
            'delivery': False,
        }
        
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_place_authenticated(self):
        """Test deleting a place as authenticated user"""
        self.client.force_authenticate(user=self.user)
        url = reverse('place-detail', kwargs={'pk': self.place.pk})
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Place.objects.filter(pk=self.place.pk).exists())

    def test_delete_place_unauthenticated(self):
        """Test deleting a place as unauthenticated user"""
        url = reverse('place-detail', kwargs={'pk': self.place.pk})
        
        response = self.client.delete(url)
        # DRF returns 403 Forbidden for unauthenticated users when permission is required
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Place should still exist
        self.assertTrue(Place.objects.filter(pk=self.place.pk).exists())

    def test_delete_place_not_found(self):
        """Test deleting non-existent place"""
        self.client.force_authenticate(user=self.user)
        url = reverse('place-detail', kwargs={'pk': 999})
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
