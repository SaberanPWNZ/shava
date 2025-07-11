from django.urls import path
from rest_framework import routers


router = routers.DefaultRouter()
urlpatterns = router.urls

# Add any additional URL patterns if needed
# urlpatterns += [
#     path('featured/', views.FeaturedNewsView.as_view(), name='featured-news'),
# ]
