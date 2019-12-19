from django.conf.urls import url
from django.urls import path,register_converter


from .pages import WikiStart
from wiki.path import WikiPath
from .views import ArticleListView,TagView,WikiPageView,PreviewView,WikiCreateView,WikiUpdateView


class WikiPathUrlConverter:
    regex = r'(?:[-a-zA-Z0-9_()]+/)*[-a-zA-Z0-9_()]+'

    def to_python(self, value):
        return WikiPath.from_url(value)

    def to_url(self, value):
        try:
            return str(WikiPath.from_obj(value))
        except AttributeError:
            return str(value)

register_converter(WikiPathUrlConverter, 'wiki')

urlpatterns = [
    url(r'^special:index$', ArticleListView.as_view(), name='wiki-index'),
    url(r'^special:preview$', PreviewView.as_view(), name='wiki-preview'),

    #path('<wiki:wiki>/edit', WikiEditView.as_view(), name='wiki-edit'),
    #path('<wiki:wiki>/new', WikiEditView.as_view(), name='wiki-new'),
    path('<wiki:wiki>/edit', WikiUpdateView.as_view(), name='wiki-edit'),
    path('<wiki:wiki>/new', WikiCreateView.as_view(), name='wiki-new'),
    path('<wiki:wiki>', WikiPageView.as_view(), name='wiki'),

    url(r'^tag:(?P<slug>[-\w_()]+)$', TagView.as_view(), name='wiki-tag'),
    url(r'^$', WikiPageView.as_view(), kwargs={'wiki':WikiStart}, name='wiki-start'),
]
