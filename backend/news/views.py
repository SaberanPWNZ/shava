import logging
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from news.models import News
from .serializers import NewsSerializer

logger = logging.getLogger("news")

# Create your views here.


class NewsViewSet(viewsets.ViewSet):
    queryset = News.objects.filter(is_published=True)
    serializer_class = NewsSerializer
    permission_classes = [IsAuthenticated]
