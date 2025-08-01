from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReviewCreateView, ReviewViewSet, ReviewCreateView

router = DefaultRouter()
router.register(r"my-reviews", ReviewViewSet, basename="my-reviews")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "reviews/<int:place_id>/",
        ReviewViewSet.as_view({"get": "list"}),
        name="place-reviews",
    ),
    path("reviews/create/", ReviewCreateView.as_view(), name="create-review"),
]
