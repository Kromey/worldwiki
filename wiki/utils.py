import re


PREFIXES = [
        "a", "an", "as", "at", "before", "but", "by", "for", "from", "is",
        "in", "into", "like", "of", "off", "on", "onto", "per", "since",
        "than", "the", "this", "that", "to", "up", "via", "with"
        ];
PREFIX_RE = re.compile(r'^(\s*({pref})\b)+'.format(pref='|'.join(PREFIXES)), re.I)

STRIP_RE = re.compile(r'[^-\w\s_()]')

WHITESPACE_RE = re.compile(r'\s+')

def slugify(text):
    text = PREFIX_RE.sub('', text)
    text = STRIP_RE.sub('', text)
    text = WHITESPACE_RE.sub('_', text.strip())

    return text

