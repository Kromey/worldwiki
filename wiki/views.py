from django.shortcuts import render
from django.views.generic import DetailView,ListView


from .models import Article


# Create your views here.

class ArticleView(DetailView):
    model = Article
    context_object_name = 'article'

