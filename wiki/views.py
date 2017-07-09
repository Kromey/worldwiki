from django.shortcuts import render
from django.views.generic import DetailView,ListView


from models import Page


# Create your views here.

class PageView(DetailView):
    model = Page
    context_object_name = 'page'

    def get_queryset(self):
        return Page.objects.filter(path=self.kwargs['path'])

