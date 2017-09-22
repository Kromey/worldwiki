from django.conf.urls import url


from .views import ArticleListView,ArticleView,TagView


urlpatterns = [
    url(r'^special:index$', ArticleListView.as_view(), name='wiki-index'),
    url(r'^(?P<slug>[-\w]+)$', ArticleView.as_view(), name='wiki'),
    url(r'^tag:(?P<slug>[-\w]+)$', TagView.as_view(), name='wiki-tag'),
    url(r'^$', ArticleView.as_view(), kwargs={'slug':'special:start'}, name='wiki-start'),
]
