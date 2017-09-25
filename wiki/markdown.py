import html
import re


import bleach
from django.urls import reverse
from django.utils import timezone
import markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import Pattern
from markdown.util import etree
from markdown.extensions.toc import TocExtension


from .utils import slugify


wikilink_pattern = r'\[\[(?:(?P<namespace>[-\w_]+):)?(?P<link>.+?)(?:\|(?P<label>.+?))?\]\]'
wikilink_re = re.compile(wikilink_pattern)


class WikiLinksExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        wikilinks = WikiLinks(wikilink_pattern)
        md.inlinePatterns.add('wikilinks', wikilinks, '>link')

class WikiLinks(Pattern):
    def handleMatch(self, m):
        namespace = m.group('namespace')
        link = m.group('link').strip()
        label = m.group('label') or link

        link = slugify(html.unescape(link.strip()))
        label = html.unescape(label.strip())

        if namespace and namespace.lower() == 'tag':
            href, title, classes = self.build_tag_link(link, label)
        else:
            href, title, classes = self.build_article_link(link, label)

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

    def build_article_link(self, slug, label):
        from .models import Article
        classes = []
        try:
            article = Article.objects.filter(is_published=True).get(slug__iexact=slug)
            slug = article.slug
            title = '{title} ({date:%b %d, %Y})'.format(
                        title = article.title,
                        date = timezone.localtime(article.published),
                        )
        except Article.DoesNotExist:
            classes.append('new')
            title = '{label} (page does not exist)'.format(label=label)

        href = reverse('wiki', args=[slug])

        return (href, title, classes)


cleaner = bleach.sanitizer.Cleaner()
converter = markdown.Markdown(
        output_format='html5',
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.smarty',
            'markdown.extensions.admonition',
            TocExtension(permalink=True, baselevel=2),
            WikiLinksExtension(),
            ],
        )
linker = bleach.linkifier.Linker(callbacks=[])


def markdown_to_html(md):
    clean_md = cleaner.clean(md)
    html = converter.reset().convert(clean_md)
    linked = linker.linkify(html)

    return linked

