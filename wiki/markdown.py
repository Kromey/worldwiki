import re


import bleach
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
import markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import Pattern
from markdown.util import etree
from markdown.extensions.toc import TocExtension


from .slug import slugify_path,WikiUrlConverter


wiki_converter = WikiUrlConverter()
wikilink_pattern = r'\[\[(?P<link>.+?)(?:\|(?P<label>.+?))?\]\]'


class EscapeHtmlExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        # Don't process raw HTML; better for our purposes than bleach
        # https://pythonhosted.org/Markdown/release-2.6.html#safe_mode-deprecated
        del md.preprocessors['html_block']
        del md.inlinePatterns['html']


class WikiLinksExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        wikilinks = WikiLinks(wikilink_pattern)
        md.inlinePatterns.add('wikilinks', wikilinks, '>link')

class WikiLinks(Pattern):
    def handleMatch(self, m):
        raw_link = m.group('link')

        wiki = wiki_converter.to_python(slugify_path(raw_link))

        label = m.group('label') or raw_link.split('/').pop()
        label = label.strip()

        if wiki.namespace and wiki.namespace.lower() == 'tag':
            href, title, classes = self.build_tag_link(wiki, label)
        else:
            href, title, classes = self.build_article_link(wiki, label)

        classes.append('wikilink')

        a = etree.Element('a')
        a.text = label
        a.set('href', href)
        a.set('class', ' '.join(classes))
        a.set('title', title)

        return a

    def build_tag_link(self, slug, label):
        from .models import Tag
        classes = ['wikitag']
        try:
            tag = Tag.objects.get(slug__iexact=slug)
            slug = tag.slug
            title = 'Pages tagged "{tag}"'.format(tag=tag.name)
        except Tag.DoesNotExist:
            classes.append('new')
            title = 'No tag "{label}"'.format(label=label)

        href = reverse('wiki-tag', args=[slug])

        return (href, title, classes)

    def build_article_link(self, wiki, label):
        from .models import Article,RedirectPage
        classes = []
        href = reverse('wiki', args=[wiki])

        try:
            article = Article.objects.published().by_url(wiki).get()
            href = article.get_absolute_url()
            title = article.title
        except Article.DoesNotExist:
            redirect = RedirectPage.objects.by_url(wiki)
            try:
                article = redirect.get().article
                href = article.get_absolute_url()
                title = article.title
            except RedirectPage.MultipleObjectsReturned:
                disambig = redirect.first()
                title = disambig.slug
            except RedirectPage.DoesNotExist:
                classes.append('new')
                title = '{label} (page does not exist)'.format(label=label)

        return (href, title, classes)


converter = markdown.Markdown(
        output_format='html5',
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.smarty',
            'markdown.extensions.admonition',
            TocExtension(permalink=True, baselevel=2),
            WikiLinksExtension(),
            EscapeHtmlExtension(),
            ],
        )
linker = bleach.linkifier.Linker(callbacks=[])


def markdown_to_html(md):
    html = converter.reset().convert(md)
    linked = linker.linkify(html)

    return linked

