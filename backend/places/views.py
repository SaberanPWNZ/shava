from rest_framework.generics import CreateAPIView  # type: ignore
from rest_framework.permissions import IsAuthenticated  # type: ignore

from backend.places.models import Place
from backend.places.serializers import PlaceCreateSerializer


class PlaceCreateView(CreateAPIView):
    """
    API endpoint that allows places to be created.
    """

    # Assuming Place is a model defined in your models.py
    queryset = Place.objects.all()
    allowed_methods = ["POST"]
    serializer_class = PlaceCreateSerializer
    permission_classes = [IsAuthenticated]
