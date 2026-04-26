from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

ARTICLE_CATEGORY_CHOICES = [
    ("guide", "Guide"),
    ("review", "Review"),
    ("news", "News"),
    ("recipe", "Recipe"),
    ("other", "Other"),
]


class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=240, unique=True, blank=True)
    excerpt = models.CharField(max_length=400, blank=True, default="")
    content = models.TextField()
    cover_image = models.ImageField(upload_to="articles/", blank=True, null=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )
    category = models.CharField(
        max_length=32, choices=ARTICLE_CATEGORY_CHOICES, default="other"
    )
    published_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at"]
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or "article"
            slug = base
            n = 1
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f"{base}-{n}"
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
