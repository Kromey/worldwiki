from django.http import Http404
from django.shortcuts import render
from django.views.generic import DetailView,ListView


from .models import Article


# Create your views here.

class ArticleView(DetailView):
    model = Article
    context_object_name = 'article'

    def get_object(self, queryset=None):
        try:
            return super().get_object(queryset)
        except Http404 as e:
            try:
                return Article.objects.get(slug='special:404')
            except Article.DoesNotExist:
                raise e

