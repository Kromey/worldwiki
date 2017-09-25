from django.http import Http404
from django.shortcuts import redirect,render
from django.views import View
from django.views.generic import DetailView,ListView


from .models import Article,Tag,RedirectPage


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
    disambiguation_template = 'wiki/article_disambiguation.html'
    show_nsfw_content = False

    def get(self, request, slug):
        self.show_nsfw_content = self.show_nsfw_content or request.session.get('show_nsfw', False)

        try:
            return self.get_article(request, slug)
        except Article.DoesNotExist:
            pass

        try:
            return self.get_redirect(request, slug)
        except RedirectPage.DoesNotExist:
            pass

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

    def get_redirect(self, request, slug):
        try:
            rp = RedirectPage.objects.get(slug=slug)

            return redirect(rp.article.get_absolute_url())
        except RedirectPage.MultipleObjectsReturned:
            articles = Article.objects.filter(redirectpage__slug=slug).order_by('title')

            return render(request, self.disambiguation_template, context={'articles':articles,'slug':slug})

