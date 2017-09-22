import re


from django import forms
from django.core.validators import RegexValidator
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse, NoReverseMatch
from django.utils import timezone
from django.utils.safestring import mark_safe


from .markdown import markdown_to_html


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
        html = markdown_to_html(self.markdown)
        return mark_safe(html)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        if self.slug.startswith('special:'):
            self.is_published = True
            self.is_nsfw = False
            self.is_spoiler = False

        if self.is_published and not self.published:
            self.published = timezone.now()

        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        try:
            return reverse('wiki', args=[self.slug])
        except NoReverseMatch:
            return None

    def view_link(self):
        url = self.get_absolute_url()

        if url:
            return '<a target="_blank" href="{url}">{url}</a>'.format(url=self.get_absolute_url())
        else:
            return self.slug
    view_link.short_description = 'view on site'
    view_link.allow_tags = True

    def get_admin_url(self):
        return reverse('admin:wiki_article_change', args=(self.pk,))

