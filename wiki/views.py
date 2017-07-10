from django.shortcuts import render
from django.views.generic import DetailView,ListView


from .models import Page


# Create your views here.

class PageView(DetailView):
    model = Page
    context_object_name = 'page'
    slug_field = 'path'
    slug_url_kwarg = 'path'

