import re


import bleach
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
import markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import Pattern
from markdown.util import etree
from markdown.extensions.toc import TocExtension


wikilink_pattern = r'\[\[(?P<link>[-\w_: ]+)(?:\|(?P<label>[^\]]+))?\]\]'
wikilink_re = re.compile(wikilink_pattern)


class WikiLinksExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        wikilinks = WikiLinks(wikilink_pattern)
        md.inlinePatterns.add('wikilinks', wikilinks, '_end')

class WikiLinks(Pattern):
    def handleMatch(self, m):
        link = m.group('link').strip()
        label = m.group('label') or link

        link = slugify(link)
        label = label.strip()

        href, title, classes = self.build_article_link(link, label)

        classes.append('wikilink')

        a = etree.Element('a')
        a.text = label
        a.set('href', href)
        a.set('class', ' '.join(classes))
        a.set('title', title)

        return a

    def build_article_link(self, slug, label):
        from .models import Article
        classes = []
        try:
            article = Article.objects.filter(is_published=True).get(slug=slug)
            title = '{title} ({date:%b %d, %Y})'.format(
                        title = article.title,
                        date = timezone.localtime(article.published),
                        )
        except Article.DoesNotExist:
            classes.append('new')
            title = label+' (page does not exist)'

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

