import bleach
import markdown
from markdown.extensions.toc import TocExtension


class Markdown:
    __converter = markdown.Markdown(
        output_format='html5',
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.smarty',
            'markdown.extensions.admonition',
            TocExtension(permalink=True, baselevel=2),
            'wiki.markdown.extensions.wikilinks',
            'wiki.markdown.extensions.escapehtml',
            ],
        )
    __linker = bleach.linkifier.Linker(callbacks=[])

    @classmethod
    def to_html(cls, md, meta=None):
        if not meta:
            meta = {}

        cls.__converter.reset()
        cls.__converter.Meta = meta
        html = cls.__converter.convert(md)
        html = cls.__linker.linkify(html)

        return html

