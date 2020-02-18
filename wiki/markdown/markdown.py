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
            'markdown.extensions.sane_lists',
            TocExtension(permalink=True, baselevel=2, title='Contents', toc_depth='2-4'),
            'wiki.markdown.extensions.strikethrough',
            'wiki.markdown.extensions.tbd',
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

        if not '[TOC]' in md and cls.__converter.toc.count('<li>') >= 3:
            lines = html.splitlines()
            for i in range(len(lines)):
                if lines[i].startswith('<h'):
                    break

            lines.insert(i, cls.__converter.toc)
            html = '\n'.join(lines)

        return html

