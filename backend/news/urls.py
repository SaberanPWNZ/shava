from django.urls import path
from rest_framework import routers
from .views import NewsViewSet

router = routers.DefaultRouter()
urlpatterns = router.urls

urlpatterns += [
    path("news/", NewsViewSet.as_view({"get": "list", "post": "create"}), name="news"),
]
