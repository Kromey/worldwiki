from django.db import models
from django.utils.safestring import mark_safe


import bleach
import markdown


cleaner = bleach.sanitizer.Cleaner()
converter = markdown.Markdown(output_format='html5')
linker = bleach.linkifier.Linker()


# Create your models here.

class Page(models.Model):
    path = models.CharField(max_length=255)
    body = models.TextField()

    @property
    def as_html(self):
        clean_body = cleaner.clean(self.body)
        html = converter.reset().convert(clean_body)
        linked = linker.linkify(html)

        return mark_safe(linked)

    def __str__(self):
        return '/' + self.path

