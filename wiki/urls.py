from django.conf.urls import url


from .views import ArticleListView,TagView,WikiPageView


urlpatterns = [
    url(r'^special:index$', ArticleListView.as_view(), name='wiki-index'),
    url(r'^(?P<slug>[-\w_()]+)$', WikiPageView.as_view(), name='wiki'),
    url(r'^tag:(?P<slug>[-\w_()]+)$', TagView.as_view(), name='wiki-tag'),
    url(r'^$', WikiPageView.as_view(), kwargs={'slug':'special:start'}, name='wiki-start'),
]
