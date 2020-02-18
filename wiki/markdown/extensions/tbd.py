from markdown.extensions import Extension
from markdown.inlinepatterns import SimpleTagInlineProcessor


TBD_RE = r'()(\((?:TBD|TODO).*?\)|\b(?:TBD|TODO)\b)\1'


class TBDExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns.register(
            TBDInlineProcessor(TBD_RE, 'span'),
            'tbd',
            50,
        )

class TBDInlineProcessor(SimpleTagInlineProcessor):
    def handleMatch(self, m, data):
        tag, start, end = super().handleMatch(m, data)

        tag.set('class', 'todo')
        return tag, start, end

def makeExtension(**kwargs):
    return TBDExtension(**kwargs)

