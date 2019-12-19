from django.conf.urls import url
from django.urls import path,register_converter


from .pages import WikiStart
from .views import ArticleListView,TagView,WikiPageView,PreviewView,WikiCreateView,WikiUpdateView


class NamespaceConverter:
    regex = r'(?:[-a-zA-Z0-9_()]+/)*'

    def to_python(self, value):
        return str(value).strip('/')

    def to_url(self, value):
        value = str(value).strip('/')

        if value:
            return value + '/'

        return ''
register_converter(NamespaceConverter, 'namespace')

class WikiSlugConverter:
    regex = r'[-a-zA-Z0-9_()]+'

    def to_python(self, value):
        return str(value)

    def to_url(self, value):
        return str(value)
register_converter(WikiSlugConverter, 'wikislug')


urlpatterns = [
    url(r'^special:index$', ArticleListView.as_view(), name='wiki-index'),
    url(r'^special:preview$', PreviewView.as_view(), name='wiki-preview'),

    #path('<wiki:wiki>/edit', WikiUpdateView.as_view(), name='wiki-edit'),
    #path('<wiki:wiki>/new', WikiCreateView.as_view(), name='wiki-new'),
    #path('<wiki:wiki>', WikiPageView.as_view(), name='wiki'),
    path('<namespace:namespace><wikislug:slug>/new', WikiCreateView.as_view(), name='wiki-new'),
    path('<namespace:namespace><wikislug:slug>/edit', WikiUpdateView.as_view(), name='wiki-edit'),
    path('<namespace:namespace><wikislug:slug>', WikiPageView.as_view(), name='wiki'),

    url(r'^tag:(?P<slug>[-\w_()]+)$', TagView.as_view(), name='wiki-tag'),
    url(r'^$', WikiPageView.as_view(), kwargs={'wiki':WikiStart}, name='wiki-start'),
]
