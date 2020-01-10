from markdown.extensions import Extension
from markdown.inlinepatterns import SimpleTagInlineProcessor


STRIKE_RE = r'(~{2})(.*?)\1'


class StrikethroughExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns.register(
            SimpleTagInlineProcessor(STRIKE_RE, 'del'),
            'strikethrough',
            150,
        )

def makeExtension(**kwargs):
    return StrikethroughExtension(**kwargs)

