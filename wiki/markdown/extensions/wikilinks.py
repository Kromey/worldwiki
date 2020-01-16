import re


from django.urls import reverse
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor


from wiki import utils


class WikiLinksExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        self.md = md
        wikilinks = WikiLinksPreprocessor(md)
        wikilinks.md = md
        md.preprocessors.register(wikilinks, 'wikilinks', 25)

class WikiLinksPreprocessor(Preprocessor):
    __WIKILINK_RE = re.compile(r'\[\[(?P<type>[a-zA-Z]+:)?(?P<link>.+?)(?:\|(?P<label>.+?))?\]\]')

    def run(self, lines):
        self.namespace = self.md.Meta.get('namespace', '').strip()
        print(self.namespace)

        return [self.processLine(line) for line in lines]

    def processLine(self, line):
        m = self.__WIKILINK_RE.search(line)

        if m is None:
            return line

        raw_link = utils.join_path(self.namespace, m.group('link'))

        namespace, page = utils.split_path(raw_link)

        label = m.group('label') or page
        label = label.strip()

        link_type = m.group('type') or ''
        link_type = link_type.rstrip(':').lower()

        if link_type == 'term' or link_type == 'def':
            (href, title, classes) = self.find_glossary_term(page)
        else:
            (href, title, classes) = self.find_linked_article(namespace, page)

        if href:
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
        else:
            # Nothing to link to, remove link
            line = line.replace(
                m[0],
                label,
            )

        # Need to go again in case there's other links
        return self.processLine(line)

    def find_linked_article(self, namespace, page):
        from wiki.models import Article
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

    def find_glossary_term(self, term):
        from wiki.models import Term
        classes = ['.wikiterm']

        try:
            term = Term.objects.get(term__iexact=term)
            href = term.get_absolute_url()
            title = term.definition
        except Term.DoesNotExist:
            href = None
            title = ''

        return href, title.replace('"', '&quot;'), ' '.join(classes)

    def build_tag_link(self, slug, label):
        from wiki.models import Tag
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


def makeExtension(**kwargs):
    return WikiLinksExtension(**kwargs)

