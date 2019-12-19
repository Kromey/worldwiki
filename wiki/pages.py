from collections import Mapping


from wiki.models import Article


class SpecialPage(Mapping):
    def __init__(self, slug, namespace=''):
        self.__namespace = namespace
        self.__slug = slug

    @property
    def namespace(self):
        return self.__namespace

    @property
    def slug(self):
        return self.__slug

    def get(self):
        return Article.objects.get(**self)

    def __getitem__(self, key):
        return getattr(self, key)

    def __iter__(self):
        yield 'slug'
        yield 'namespace'

    def __len__(self):
        return 2


Error404 = SpecialPage('Error404')
WikiStart = SpecialPage('start')
WikiSidebar = SpecialPage('sidebar')

