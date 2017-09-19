import re


from django import forms
from django.core.validators import RegexValidator
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe


import bleach
import markdown
from markdown.extensions.toc import TocExtension


from .markdown import WikiLinksExtension


cleaner = bleach.sanitizer.Cleaner()
converter = markdown.Markdown(
        output_format='html5',
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.smarty',
            'markdown.extensions.admonition',
            TocExtension(permalink=True),
            WikiLinksExtension(),
            ],
        )
linker = bleach.linkifier.Linker()


slug_re = re.compile(r'^[-a-zA-Z0-9_:]+$')
validate_slug = RegexValidator(slug_re, 'Please enter a valid slug consisting of letters, numbers, underscores, hyphens, or colons', 'invalid')

class WikiSlugFormField(forms.SlugField):
    default_validators = [validate_slug,]


class WikiSlugField(models.SlugField):
    validators = [validate_slug,]

    def formfield(self, **kwargs):
        return super().formfield(form_class=WikiSlugFormField, **kwargs)


# Create your models here.

class Article(models.Model):
    title = models.CharField('article title', max_length=50)
    slug = WikiSlugField(unique=True)
    published = models.DateTimeField(null=True, default=None)
    edited = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField('publish?', default=False)
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

        if self.is_published and not self.published:
            self.published = timezone.now()

        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('wiki', args=[self.slug])

    def view_link(self):
        return '<a target="_blank" href="{url}">{url}</a>'.format(url=self.get_absolute_url())
    view_link.short_description = 'view on site'
    view_link.allow_tags = True

