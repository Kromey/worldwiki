from django.http import Http404
from django.shortcuts import render
from django.views.generic import DetailView,ListView


from .models import Article,Tag


# Create your views here.

class TagView(DetailView):
    model = Tag
    context_object_name = 'tag'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['articles'] = self.object.articles.order_by('slug')

        return context


class ArticleView(DetailView):
    context_object_name = 'article'
    show_nsfw_content = False
    nsfw_template_name = 'wiki/article_nsfw.html'

    def get_queryset(self):
        if self.request.user.has_perm('wiki.change_article'):
            return Article.objects.all()
        else:
            return Article.objects.filter(is_published=True)

    def get_object(self, queryset=None):
        try:
            return super().get_object(queryset)
        except Http404 as e:
            try:
                return Article.objects.get(slug='special:404')
            except Article.DoesNotExist:
                raise e

    def get_template_names(self):
        names = super().get_template_names()

        if self.object.is_nsfw and not self.show_nsfw_content:
            names.insert(0, self.nsfw_template_name)

        return names

    def get(self, request, *args, **kwargs):
        self.show_nsfw_content = self.show_nsfw_content or request.session.get('show_nsfw', False)

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.POST.get('show-me'):
            self.show_nsfw_content = True
            if request.POST.get('remember'):
                request.session['show_nsfw'] = True

        return self.get(request, *args, **kwargs)

