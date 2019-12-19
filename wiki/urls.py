from django.urls import path,register_converter


from wiki.pages import WikiStart
from wiki.views import ArticleListView,TagView,WikiPageView,PreviewView,WikiCreateView,WikiUpdateView


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
    path('special:index', ArticleListView.as_view(), name='wiki-index'),
    path('special:preview', PreviewView.as_view(), name='wiki-preview'),

    path('<namespace:namespace><wikislug:slug>/new', WikiCreateView.as_view(), name='wiki-new'),
    path('<namespace:namespace><wikislug:slug>/edit', WikiUpdateView.as_view(), name='wiki-edit'),
    path('<namespace:namespace><wikislug:slug>', WikiPageView.as_view(), name='wiki'),

    path('tag:<wikislug:slug>', TagView.as_view(), name='wiki-tag'),
    path('', WikiPageView.as_view(), kwargs=WikiStart, name='wiki-start'),
]
