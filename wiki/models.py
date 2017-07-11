from django.db import models
from django.utils.safestring import mark_safe


import bleach
import markdown


# Create your models here.

class Page(models.Model):
    path = models.CharField(max_length=255)
    body = models.TextField()

    @property
    def as_html(self):
        clean_body = bleach.clean(self.body)
        html = markdown.markdown(clean_body)
        linked = bleach.linkify(html)

        return mark_safe(linked)

    def __str__(self):
        return '/' + self.path

