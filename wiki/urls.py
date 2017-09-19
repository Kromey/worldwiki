from django.conf.urls import url


from .views import ArticleView


urlpatterns = [
    url(r'^(?P<slug>[-\w:]+)/?$', ArticleView.as_view(), name='wiki'),
]
