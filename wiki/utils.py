import re


from django.core.exceptions import ValidationError


__SLUG = re.compile(r'^[-a-z0-9_()]+$', re.I)
__NAMESPACE = re.compile(r'^(?:[-a-z0-9_()]+/)*[-a-z0-9_()]+$', re.I)

__PREFIXES = re.compile(r'^(\s*({prefixes})\b)+'.format(
    prefixes='|'.join(
        [
            "a", "an", "as", "at", "before", "but", "by", "for", "from", "is",
            "in", "into", "like", "of", "off", "on", "onto", "per", "since",
            "than", "the", "this", "that", "to", "up", "via", "with",
        ]
    )
), re.I)

__SLUG_CLEAN = re.compile(r'[^-a-z0-9\s_()]', re.I)
__WHITESPACE = re.compile(r'\s+')


def validate_slug(slug):
    if __SLUG.match(slug) is None:
        raise ValidationError('"{}" is not a valid slug'.format(slug))

def validate_namespace(namespace):
    # Special case: '' is a valid namespace
    if namespace != '':
        for n in namespace.split('/'):
            try:
                validate_slug(n)
            except ValidationError as e:
                raise ValidationError('"{}" is not a valid namespace'.format(namespace)) from e

def slugify(slug):
    slug = __PREFIXES.sub('', slug)
    slug = __SLUG_CLEAN.sub('', slug)
    slug = slug.strip()
    slug = __WHITESPACE.sub('_', slug)

    return slug

def slugify_namespace(namespace):
    namespace = namespace.strip('/').split('/')
    return '/'.join(map(slugify, namespace))

def split_path(path):
    path = path.lstrip('/').rsplit('/', 1)

    slug = path.pop()

    try:
        namespace = path.pop()
    except IndexError:
        namespace = ''

    return (namespace, slug)

def join_path(path, *paths):
    for p in paths:
        # Special case: p is absolute
        if p.startswith('/'):
            path = p.strip('/')
            continue

        # './' is relative, but so is nothing
        if p.startswith('./'):
            p = p[2:]

        # '../' moves us up a namespace
        while p.startswith('../'):
            path = namespace(path)
            p = p[3:]

        path = '/'.join([path, p]).strip('/')

    return path

def namespace(path):
    return split_path(path)[0]

