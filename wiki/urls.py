from django.conf.urls import url


from .views import ArticleView,TagView


urlpatterns = [
    url(r'^(?P<slug>[-\w]+)$', ArticleView.as_view(), name='wiki'),
    url(r'^tag:(?P<slug>[-\w]+)$', TagView.as_view(), name='wiki-tag'),
    url(r'^$', ArticleView.as_view(), kwargs={'slug':'special:start'}, name='wiki-start'),
]
