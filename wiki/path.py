import re


from django.core.exceptions import ValidationError


class WikiPath:
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

    def __init__(self, slug, namespace=''):
        try:
            WikiPath.validate_slug(slug)
            WikiPath.validate_namespace(namespace)
        except ValidationError as e:
            raise ValueError('Invalid slug or namespace') from e

        self.__slug = slug
        self.__namespace = namespace

    @classmethod
    def from_url(cls, url):
        slug, namespace = cls._split_url(url)

        if namespace:
            return cls(slug, namespace)
        else:
            return cls(slug)

    @classmethod
    def from_title(cls, url):
        slug, namespace = cls._split_url(url)

        slug = cls.transform_slug(slug)

        if namespace:
            namespace = cls.transform_namespace(namespace)

            return cls(slug, namespace)
        else:
            return cls(slug)

    @classmethod
    def from_obj(cls, obj):
        return cls(obj.slug, obj.namespace)

    @staticmethod
    def _split_url(url):
        url = url.lstrip('/').rsplit('/', 1)

        slug = url.pop()

        try:
            namespace = url.pop()
        except IndexError:
            namespace = None

        return (slug, namespace)

    @staticmethod
    def validate_slug(slug):
        if WikiPath.__SLUG.match(slug) is None:
            raise ValidationError('"{}" is not a valid slug'.format(slug))

    @staticmethod
    def validate_namespace(namespace):
        # Special case: '' is a valid namespace
        if namespace != '':
            for n in namespace.split('/'):
                try:
                    WikiPath.validate_slug(n)
                except ValidationError as e:
                    raise ValidationError('"{}" is not a valid namespace'.format(namespace)) from e

    @staticmethod
    def transform_slug(slug):
        slug = WikiPath.__PREFIXES.sub('', slug)
        slug = WikiPath.__SLUG_CLEAN.sub('', slug)
        slug = slug.strip()
        slug = WikiPath.__WHITESPACE.sub('_', slug)

        return slug

    @staticmethod
    def transform_namespace(namespace):
        namespace = namespace.lstrip('/').split('/')
        return '/'.join(map(WikiPath.transform_slug, namespace))

    @property
    def slug(self):
        return self.__slug

    @property
    def namespace(self):
        return self.__namespace

    def to_url(self):
        return '{namespace}/{slug}'.format(
            namespace = self.namespace,
            slug = self.slug,
        ).lstrip('/')

    def __str__(self):
        return self.to_url()

    def __repr__(self):
        if self.namespace:
            return 'WikiPath("{slug}", "{namespace}")'.format(
                slug = self.slug,
                namespace = self.namespace,
            )
        else:
            return 'WikiPath("{slug}")'.format(
                slug = self.slug,
            )
