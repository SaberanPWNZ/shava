from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from reviews.models import Review
from places.models import Place
from .models import Achievement, UserRating, UserAchievement

User = get_user_model()


class AchievementModelTest(TestCase):
    """Test cases for Achievement model."""

    def setUp(self):
        self.achievement = Achievement.objects.create(
            name="Newbie Shaurmie",
            description="Write your first 10 reviews",
            reviews_required=10,
            icon="🏆"
        )

    def test_achievement_creation(self):
        """Test achievement creation with valid data."""
        self.assertEqual(self.achievement.name, "Newbie Shaurmie")
        self.assertEqual(self.achievement.reviews_required, 10)
        self.assertTrue(self.achievement.is_active)

    def test_achievement_str(self):
        """Test achievement string representation."""
        expected = "Newbie Shaurmie (Requires 10 reviews)"
        self.assertEqual(str(self.achievement), expected)


class UserRatingModelTest(TestCase):
    """Test cases for UserRating model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.user_rating = UserRating.objects.create(
            user=self.user,
            total_reviews=5,
            average_score_given=Decimal('7.50'),
            level=2,
            experience_points=50
        )

    def test_user_rating_creation(self):
        """Test user rating creation with valid data."""
        self.assertEqual(self.user_rating.user, self.user)
        self.assertEqual(self.user_rating.total_reviews, 5)
        self.assertEqual(self.user_rating.level, 2)

    def test_user_rating_str(self):
        """Test user rating string representation."""
        expected = "testuser - Level 2 (5 reviews)"
        self.assertEqual(str(self.user_rating), expected)


class UserAchievementModelTest(TestCase):
    """Test cases for UserAchievement model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.achievement = Achievement.objects.create(
            name="Newbie Shaurmie",
            description="Write your first 10 reviews",
            reviews_required=10
        )
        self.user_achievement = UserAchievement.objects.create(
            user=self.user,
            achievement=self.achievement
        )

    def test_user_achievement_creation(self):
        """Test user achievement creation."""
        self.assertEqual(self.user_achievement.user, self.user)
        self.assertEqual(self.user_achievement.achievement, self.achievement)

    def test_user_achievement_unique_constraint(self):
        """Test that a user can't earn the same achievement twice."""
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            UserAchievement.objects.create(
                user=self.user,
                achievement=self.achievement
            )

    def test_user_achievement_str(self):
        """Test user achievement string representation."""
        expected = "testuser earned Newbie Shaurmie"
        self.assertEqual(str(self.user_achievement), expected)


class RatingSignalsTest(TestCase):
    """Test cases for rating signals."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        # Create a simple place for reviews
        self.place = Place.objects.create(
            name="Test Shawarma Place",
            address="Test Address"
        )
        # Create an achievement
        self.achievement = Achievement.objects.create(
            name="First Review",
            description="Write your first review",
            reviews_required=1
        )

    def test_user_rating_created_on_first_review(self):
        """Test that UserRating is created when user writes first review."""
        # Initially no UserRating should exist
        self.assertFalse(UserRating.objects.filter(user=self.user).exists())

        # Create a review
        Review.objects.create(
            place=self.place,
            author=self.user,
            score=Decimal('8.0'),
            comment="Great shawarma!"
        )

        # Check that UserRating was created
        user_rating = UserRating.objects.get(user=self.user)
        self.assertEqual(user_rating.total_reviews, 1)
        self.assertEqual(user_rating.experience_points, 10)
        self.assertEqual(user_rating.level, 1)

    def test_achievement_awarded_on_review_count(self):
        """Test that achievement is awarded when review count threshold is met."""
        # Create a review
        Review.objects.create(
            place=self.place,
            author=self.user,
            score=Decimal('8.0'),
            comment="Great shawarma!"
        )

        # Check that achievement was awarded
        user_achievement = UserAchievement.objects.get(
            user=self.user,
            achievement=self.achievement
        )
        self.assertIsNotNone(user_achievement)


class RatingAPITest(APITestCase):
    """Test cases for rating API endpoints."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
            is_staff=True,
            is_superuser=True
        )
        self.achievement = Achievement.objects.create(
            name="Test Achievement",
            description="Test description",
            reviews_required=5
        )

    def test_achievement_list_requires_authentication(self):
        """Test that achievement list requires authentication."""
        url = reverse('achievement-list')
        response = self.client.get(url)
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
        )

    def test_achievement_list_authenticated(self):
        """Test achievement list with authenticated user."""
        self.client.force_authenticate(user=self.user)
        url = reverse('achievement-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_achievement_create_requires_admin(self):
        """Test that creating achievements requires admin permissions."""
        self.client.force_authenticate(user=self.user)
        url = reverse('achievement-list')
        data = {
            'name': 'New Achievement',
            'description': 'New description',
            'reviews_required': 10
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_achievement_create_admin(self):
        """Test achievement creation by admin user."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('achievement-list')
        data = {
            'name': 'New Achievement',
            'description': 'New description',
            'reviews_required': 10
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_rating_me_endpoint(self):
        """Test the user rating 'me' endpoint."""
        # Create user rating
        UserRating.objects.create(
            user=self.user,
            total_reviews=5,
            level=2
        )

        self.client.force_authenticate(user=self.user)
        url = reverse('userrating-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_reviews'], 5)
        self.assertEqual(response.data['level'], 2)

    def test_user_rating_me_not_found(self):
        """Test the user rating 'me' endpoint when no rating exists."""
        self.client.force_authenticate(user=self.user)
        url = reverse('userrating-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
