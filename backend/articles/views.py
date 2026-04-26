from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser

from articles.models import Article
from articles.serializers import ArticleDetailSerializer, ArticleListSerializer


class ArticleViewSet(viewsets.ModelViewSet):
    """Articles are publicly readable (when published); admin-only for writes."""

    queryset = Article.objects.all()
    lookup_field = "slug"
    search_fields = ["title", "excerpt", "content"]
    ordering_fields = ["published_at", "created_at", "title"]

    def get_serializer_class(self):
        if self.action == "list":
            return ArticleListSerializer
        return ArticleDetailSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        # `select_related("author")` avoids an N+1 in `get_author_name`.
        qs = Article.objects.select_related("author")
        params = self.request.query_params

        # Non-staff users only see published articles.
        if not (self.request.user.is_authenticated and self.request.user.is_staff):
            qs = qs.filter(is_published=True)

        category = params.get("category")
        if category:
            qs = qs.filter(category=category)
        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
