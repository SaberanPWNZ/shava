from django.db import models


class News(models.Model):
    title = models.CharField(max_length=200, verbose_name="Title")
    text = models.TextField(verbose_name="Content")
    published_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Published Date"
    )
    author = models.CharField(max_length=100, verbose_name="Author")
    image = models.ImageField(upload_to="news_images/", null=True, blank=True)
    is_published = models.BooleanField(default=False, verbose_name="Is Published")
