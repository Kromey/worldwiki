from django.conf.urls import url


from .views import ArticleListView,TagView,WikiPageView,PreviewView,WikiEditView


urlpatterns = [
    url(r'^special:index$', ArticleListView.as_view(), name='wiki-index'),
    url(r'^special:preview$', PreviewView.as_view(), name='wiki-preview'),

    url(r'^(?P<slug>[-\w_()]+)$', WikiPageView.as_view(), name='wiki'),
    url(r'^(?P<slug>[-\w:_()]+)/edit$', WikiEditView.as_view(), name='wiki-edit'),
    url(r'^(?P<slug>[-\w_()]+)/new$', WikiEditView.as_view(), name='wiki-new'),

    url(r'^tag:(?P<slug>[-\w_()]+)$', TagView.as_view(), name='wiki-tag'),
    url(r'^$', WikiPageView.as_view(), kwargs={'slug':'special:start'}, name='wiki-start'),
]
