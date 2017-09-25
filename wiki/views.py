from django.http import Http404
from django.shortcuts import render
from django.views import View
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


class ArticleListView(ListView):
    queryset = Article.objects.filter(is_published=True).exclude(slug__startswith='special:').order_by('slug')
    context_object_name = 'articles'


class WikiPageView(View):
    article_template = 'wiki/article_detail.html'
    nsfw_template = 'wiki/article_nsfw.html'
    show_nsfw_content = False

    def get(self, request, slug):
        self.show_nsfw_content = self.show_nsfw_content or request.session.get('show_nsfw', False)

        try:
            return self.get_article(request, slug)
        except Article.DoesNotExist:
            return self.get_article(request, 'special:404')

    def post(self, request, *args, **kwargs):
        if request.POST.get('show-me'):
            self.show_nsfw_content = True
            if request.POST.get('remember'):
                request.session['show_nsfw'] = True

        return self.get(request, *args, **kwargs)

    def get_article(self, request, slug):
        if self.request.user.has_perm('wiki.change_article'):
            qs = Article.objects
        else:
            qs = Article.objects.filter(is_published=True)

        article = qs.get(slug=slug)

        if article.is_nsfw and not self.show_nsfw_content:
            return render(request, self.nsfw_template, context={'article':article})
        else:
            return render(request, self.article_template, context={'article':article})

