import re


from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse, NoReverseMatch
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe


from .slug import WikiSlugField,WikiNamespaceField,slugify
from .markdown import markdown_to_html


# Create your models here.


class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = WikiSlugField(unique=True, blank=True)
    description = models.TextField('tag description', help_text='Formatted using Markdown', blank=True)

    @property
    def html(self):
        html = markdown_to_html(self.description)
        return mark_safe(html)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        return super().save(*args, **kwargs)

    class Meta:
        ordering = ('name',)


class Article(models.Model):
    title = models.CharField('article title', max_length=50)
    namespace = WikiNamespaceField(blank=True, default='')
    slug = WikiSlugField(unique=True, blank=True)
    published = models.DateTimeField(null=True, default=None)
    edited = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField('publish?', default=False)
    is_nsfw = models.BooleanField('NSFW?', default=False)
    is_spoiler = models.BooleanField('spoiler?', default=False)
    tags = models.ManyToManyField(
            Tag,
            related_name='articles',
            related_query_name='article',
            blank=True,
            )
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

        self.validate_unique()

        if self.is_published and not self.published:
            self.published = timezone.now()

        return super().save(*args, **kwargs)

    def clean(self):
        super().clean()

        if not self.slug:
            self.slug = slugify(self.title)

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude)

        qs = Article.objects.filter(slug__iexact=self.slug)
        if self.pk:
            qs = qs.exclude(pk=self.pk)

        if qs.exists():
            raise ValidationError({'slug':'Slug must be unique (case-insensitive)'})

    def get_absolute_url(self):
        try:
            return reverse('wiki', args=[self.slug])
        except NoReverseMatch:
            return None

    def view_link(self):
        url = self.get_absolute_url()

        if url:
            return format_html(
                '<a target="_blank" href="{}">{}</a>',
                self.get_absolute_url(),
                self.get_absolute_url(),
            )
        else:
            return self.slug
    view_link.short_description = 'view on site'

    def get_admin_url(self):
        return reverse('admin:wiki_article_change', args=(self.pk,))

    class Meta:
        ordering = ('slug',)


class RedirectPage(models.Model):
    title = models.CharField('page title', max_length=50)
    slug = WikiSlugField(blank=True)
    article = models.ForeignKey(
            Article,
            on_delete=models.CASCADE,
            related_name='redirectpages',
            related_query_name='redirectpage',
            )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        return super().save(*args, **kwargs)

    def __str__(self):
        return '{title} ⇒ {target}'.format(title=self.title, target=self.article.title)

