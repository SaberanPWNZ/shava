from rest_framework.routers import SimpleRouter

from places_menu.views import PlaceMenuViewSet

router = SimpleRouter()
router.register(r"", PlaceMenuViewSet, basename="place-menu")

urlpatterns = router.urls
