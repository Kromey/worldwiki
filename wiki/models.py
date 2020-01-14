import re
from urllib.parse import parse_qsl,urlencode,urlsplit,urlunsplit


from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse, NoReverseMatch
from django.utils import timezone
from django.utils.safestring import mark_safe


from wiki import utils
from wiki.fields import WikiSlugField,WikiNamespaceField
from wiki.markdown import Markdown


# Create your models here.


class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = WikiSlugField(unique=True, blank=True)
    description = models.TextField('tag description', help_text='Formatted using Markdown', blank=True)

    @property
    def html(self):
        html = Markdown.to_html(self.description)
        return mark_safe(html)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = utils.slugify(self.name)

        return super().save(*args, **kwargs)

    class Meta:
        ordering = ('name',)


class Article(models.Model):
    title = models.CharField('article title', max_length=50)
    namespace = WikiNamespaceField(blank=True, default='')
    slug = WikiSlugField(blank=True)
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
        meta = {
            'title': self.title,
            'published': self.published,
            'namespace': self.namespace,
        }

        html = Markdown.to_html(self.markdown, meta)
        return mark_safe(html)

    REDIRECT_RE = re.compile(r'^\[\[REDIRECT:(?P<redirect>.*?)\]\]', re.I)

    @property
    def is_redirect(self):
        return self.REDIRECT_RE.match(self.markdown.strip()) is not None

    def get_redirect(self, qs=None):
        m = self.REDIRECT_RE.match(self.markdown.strip())

        if m is None:
            return None

        url = m.group('redirect')
        # Prepend current namespace if redirect URL is not absolute
        url = utils.join_path(self.namespace, url)

        # Get and slugify namespace and slug from URL
        namespace, slug = utils.split_path(url)
        slug = utils.slugify(slug)
        namespace = utils.slugify_namespace(namespace)

        if qs is None:
            qs = Article.objects.filter(is_published=True)

        return qs.get(namespace=namespace, slug=slug)

    def _sticky_url(self, url):
        url = urlsplit(url)

        query = parse_qsl(url.query)
        query.append(('redirect','no'))

        url = url._replace(query=urlencode(query))

        return urlunsplit(url)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = utils.slugify(self.title)

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
            self.slug = utils.slugify(self.title)

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude)

        qs = Article.objects.filter(slug=self.slug, namespace=self.namespace)
        if self.pk:
            qs = qs.exclude(pk=self.pk)

        if qs.exists():
            raise ValidationError({'slug':'Namespace+slug must be unique (case-insensitive)'})

    def get_absolute_url(self):
        return self.__reverse('wiki')

    def get_edit_url(self):
        return self.__reverse('wiki-edit')

    def get_move_url(self):
        return self.__reverse('wiki-move')

    def __reverse(self, url):
        try:
            return reverse(url, args=[self.namespace, self.slug])
        except NoReverseMatch:
            return None

    def get_admin_url(self):
        return reverse('admin:wiki_article_change', args=(self.pk,))

    class Meta:
        ordering = ('slug',)


class Term(models.Model):
    term = models.CharField(max_length=250, unique=True)
    definition = models.TextField()

    @property
    def anchor(self):
        return utils.slugify(self.term)

    def get_absolute_url(self):
        return '{url}#{anchor}'.format(
            url = reverse('wiki-glossary'),
            anchor = self.anchor,
        )

    class Meta:
        ordering = ('term',)


