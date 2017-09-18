from django.db import models
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe


import bleach
import markdown
from markdown.extensions.toc import TocExtension


cleaner = bleach.sanitizer.Cleaner()
converter = markdown.Markdown(
        output_format='html5',
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.smarty',
            'markdown.extensions.admonition',
            TocExtension(permalink=True),
            ],
        )
linker = bleach.linkifier.Linker()


# Create your models here.

class Article(models.Model):
    title = models.CharField('article title', max_length=50)
    slug = models.SlugField(unique=True)
    published = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    is_nsfw = models.BooleanField('NSFW?', default=False)
    is_spoiler = models.BooleanField('spoiler?', default=False)
    markdown = models.TextField('article content', help_text='Formatted using Markdown')

    @property
    def html(self):
        clean_body = cleaner.clean(self.markdown)
        html = converter.reset().convert(clean_body)
        linked = linker.linkify(html)

        return mark_safe(linked)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        return super().save(*args, **kwargs)

