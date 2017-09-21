import re


from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from markdown.extensions import Extension
from markdown.inlinepatterns import Pattern
from markdown.util import etree


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

        href = reverse('wiki', args=[link])

        a = etree.Element('a')

        from .models import Article
        classes = ['wikilink',]
        try:
            article = Article.objects.filter(is_published=True).get(slug=link)
            a.set(
                    'title',
                    '{title} ({date:%b %d, %Y})'.format(
                        title = article.title,
                        date = timezone.localtime(article.published),
                        )
                    )
        except Article.DoesNotExist:
            classes.append('new')
            a.set('title', label+' (page does not exist)')

        a.text = label
        a.set('href', href)
        a.set('class', ' '.join(classes))

        return a

