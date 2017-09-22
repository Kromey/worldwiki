import re


from django.template import defaultfilters


SKIPPED_PREFIXES = [
        "a", "an", "as", "at", "before", "but", "by", "for", "from", "is",
        "in", "into", "like", "of", "off", "on", "onto", "per", "since",
        "than", "the", "this", "that", "to", "up", "via", "with"
        ];
SKIPPED_RE = re.compile(r'^({pref})\b'.format(pref='|'.join(SKIPPED_PREFIXES)), re.I)

def slugify(text):
    text = SKIPPED_RE.sub('', text)

    return defaultfilters.slugify(text)

