import logging
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from news.models import News
from news.serializers import NewsSerializer

logger = logging.getLogger("news")

# Create your views here.


class NewsViewSet(viewsets.ViewSet):
    queryset = News.objects.filter(is_published=True)
    serializer_class = NewsSerializer
