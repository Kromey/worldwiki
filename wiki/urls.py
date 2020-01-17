from django.urls import path,register_converter


from wiki.pages import WikiStart
from wiki import views


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
    path('glossary', views.GlossaryView.as_view(), name='wiki-glossary'),
    path('glossary;action=edit', views.TermCreateView.as_view(), name='wiki-term-new'),
    path('glossary;action=edit&id=<int:pk>', views.TermEditView.as_view(), name='wiki-term-edit'),

    path('special:index', views.ArticleListView.as_view(), name='wiki-index'),
    path('special:preview', views.PreviewView.as_view(), name='wiki-preview'),

    path('tag:<wikislug:slug>', views.TagView.as_view(), name='wiki-tag'),
    path('tag:<wikislug:slug>;action=edit', views.TagEditView.as_view(), name='wiki-tag-edit'),

    path('<namespace:namespace><wikislug:slug>;action=create', views.WikiCreateView.as_view(), name='wiki-new'),
    path('<namespace:namespace><wikislug:slug>;action=edit', views.WikiUpdateView.as_view(), name='wiki-edit'),
    path('<namespace:namespace><wikislug:slug>;action=move', views.WikiMoveView.as_view(), name='wiki-move'),
    path('<namespace:namespace><wikislug:slug>', views.WikiPageView.as_view(), name='wiki'),
    path('', views.WikiPageView.as_view(), kwargs=WikiStart, name='wiki-start'),
]
