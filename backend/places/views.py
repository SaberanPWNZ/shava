from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView  # type: ignore
from rest_framework.permissions import IsAuthenticated  # type: ignore

from places.models import Place, PlaceRating
from places.serializers import PlaceCreateSerializer, PlaceRatingSerializer


class PlaceCreateView(CreateAPIView):
    """
    API endpoint that allows places to be created.
    """

    queryset = Place.objects.all()
    allowed_methods = ["POST"]
    serializer_class = PlaceCreateSerializer
    permission_classes = [IsAuthenticated]


class PlaceRatingViewSet(viewsets.ModelViewSet):
    queryset = PlaceRating.objects.all()
    serializer_class = PlaceRatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PlaceRating.objects.filter(user=self.request.user)

    @action(detail=False, methods=["post"], url_path="rate-place")
    def rate_place(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
