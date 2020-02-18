import bleach
from bleach_whitelist import markdown_tags,markdown_attrs
import markdown
from markdown.extensions.toc import TocExtension


markdown_tags.append('del')
markdown_attrs['*'].append('class')

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
            ],
        )
    __linker = bleach.linkifier.Linker(callbacks=[])

    @classmethod
    def to_html(cls, md, meta=None):
        if not meta:
            meta = {}

        # Set up our metadata
        cls.__converter.reset()
        cls.__converter.Meta = meta
        # Convert the Markdown to HTML
        html = cls.__converter.convert(md)

        # Sanitize the HTML
        # Don't use a global class instance, as it's not thread-safe
        html = bleach.clean(html, markdown_tags, markdown_attrs)
        # Linkify any additional URLs in the text
        html = cls.__linker.linkify(html)

        # If we have at least 3 headers and no explicit TOC token, add the TOC
        if not '[TOC]' in md and cls.__converter.toc.count('<li>') >= 3:
            lines = html.splitlines()
            for i in range(len(lines)):
                # Look for the first header
                # We know we'll find one because there's at least 3
                if lines[i].startswith('<h'):
                    break

            # Insert the TOC before the first header
            lines.insert(i, cls.__converter.toc)
            # Recombine the lines into a single document
            html = '\n'.join(lines)

        return html

