import re


from django.urls import reverse
from markdown.extensions import Extension
from markdown.inlinepatterns import Pattern
from markdown.util import etree


wikilink_pattern = r'\[\[(?P<link>[-\w_:]+)(?:\|(?P<label>[^\]]+))?\]\]'
wikilink_re = re.compile(wikilink_pattern)


class WikiLinksExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        wikilinks = WikiLinks(wikilink_pattern)
        md.inlinePatterns.add('wikilinks', wikilinks, '_end')

class WikiLinks(Pattern):
    def handleMatch(self, m):
        link = m.group('link').strip()
        label = m.group('label') or link
        label = label.strip()

        href = reverse('wiki', args=[link])

        a = etree.Element('a')
        a.text = label
        a.set('href', href)
        a.set('class', 'wikilink')

        return a

