import re


import bleach
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
import markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from markdown.util import etree
from markdown.extensions.toc import TocExtension


from wiki import utils


wikilink_re = re.compile(r'\[\[(?P<type>[a-zA-Z]+:)?(?P<link>.+?)(?:\|(?P<label>.+?))?\]\]')


class EscapeHtmlExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        # Don't process raw HTML; better for our purposes than bleach
        # https://pythonhosted.org/Markdown/release-2.6.html#safe_mode-deprecated
        del md.preprocessors['html_block']
        del md.inlinePatterns['html']


class WikiLinksExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        self.md = md
        wikilinks = WikiLinksPreprocessor(md)
        wikilinks.md = md
        md.preprocessors.register(wikilinks, 'wikilinks', 25)

class WikiLinksPreprocessor(Preprocessor):
    def run(self, lines):
        self.base_url = self.md.Meta.get('baseurl', [''])[0].strip()

        return [self.processLine(line) for line in lines]

    def processLine(self, line):
        m = wikilink_re.search(line)

        if m is None:
            return line

        raw_link = self.rebase_link(m.group('link'))

        namespace, page = utils.split_path(raw_link)

        label = m.group('label') or page
        label = label.strip()

        (href, title, classes) = self.find_linked_article(namespace, page)

        if m.group('type'):
            classes += ' .' + m.group('type').rstrip(':').lower()

        line = line.replace(
            m[0],
            '[{label}]({href}){{: {classes} title="{title}" }}'.format(
                label=label,
                href=href,
                classes=classes,
                title=title,
            ),
        )

        # Need to go again in case there's other links
        return self.processLine(line)

    def rebase_link(self, link):
        # Link is an absolute path
        if link.startswith('/'):
            return link.lstrip('/')

        base = self.base_url

        # If the link starts with './', it's relative to this page
        if link.startswith('./'):
            return base + link.lstrip('.')

        # Doesn't start with './', so it's relative to the current namespace
        base = self.namespace(base)

        # '../' is a reference to the parent namespace
        while link.startswith('../'):
            link = link[3:]
            base = self.namespace(base)

        return '/'.join([base, link]).lstrip('/')

    def namespace(self, link):
        return '/'.join(link.split('/')[:-1])

    def find_linked_article(self, namespace, page):
        from .models import Article
        classes = ['.wikilink']

        slug = utils.slugify(page)
        namespace = utils.slugify_namespace(namespace)

        try:
            article = Article.objects.get(is_published=True, slug=slug, namespace=namespace)
            href = article.get_absolute_url()
            title = article.title
        except Article.DoesNotExist:
            classes.append('.new')
            href = reverse('wiki', args=[namespace, slug])
            title = '{page} (page does not exist)'.format(page=page)

        return href, title.replace('"', '&quot;'), ' '.join(classes)

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


converter = markdown.Markdown(
        output_format='html5',
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.smarty',
            'markdown.extensions.admonition',
            'markdown.extensions.meta',
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

