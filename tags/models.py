from django.db import models
from blog.models import Blog, ElectNew


class ManagerTag(models.Model):
    name = models.CharField(max_length=100, verbose_name="name")
    blog = models.ManyToManyField(Blog, blank=True, related_name='blog_tags')
    new = models.ManyToManyField(ElectNew, blank=True, related_name='new_tags')
    parent = models.ForeignKey("self", blank=True, null=True, related_name='+', on_delete=models.CASCADE, verbose_name="Родитель")

    class Meta:
        verbose_name = "Наш тег"
        verbose_name_plural = "Наши теги"

    def __str__(self):
        return self.name
