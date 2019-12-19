from django.http import Http404,HttpResponse
from django.shortcuts import get_object_or_404,redirect,render
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views import View
from django.views.generic import DetailView,ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView,UpdateView


from .forms import ArticleForm
from .markdown import markdown_to_html
from .models import Article,Tag
from .pages import Error404


# Create your views here.

class TagView(TemplateView):
    model = Tag
    context_object_name = 'tag'
    template_name = 'wiki/article_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        tag = get_object_or_404(Tag, slug=self.kwargs['slug'])

        context['articles'] = tag.articles.all()
        context['title'] = 'Articles tagged "{name}"'.format(name=tag.name)
        context['description'] = tag.html

        return context


class ArticleListView(ListView):
    queryset = Article.objects.filter(is_published=True).exclude(slug__startswith='special:')
    context_object_name = 'articles'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = 'All Pages on Langthil'

        return context


class WikiPageView(View):
    article_template = 'wiki/article_detail.html'
    nsfw_template = 'wiki/article_nsfw.html'
    disambiguation_template = 'wiki/article_list.html'
    show_nsfw_content = False
    create_url = None

    def get(self, request, wiki):
        self.show_nsfw_content = self.show_nsfw_content or request.session.get('show_nsfw', False)

        try:
            return self.get_article(request, wiki)
        except Article.DoesNotExist:
            pass

        self.create_url = reverse('wiki-new', kwargs={'wiki':wiki})
        return self.get_article(request, Error404)

    def post(self, request, *args, **kwargs):
        if request.POST.get('show-me'):
            self.show_nsfw_content = True
            if request.POST.get('remember'):
                request.session['show_nsfw'] = True

        return self.get(request, *args, **kwargs)

    def get_article(self, request, wiki):
        if self.request.user.has_perm('wiki.change_article') or 'preview' in self.request.GET:
            qs = Article.objects
        else:
            qs = Article.objects.published()

        article = qs.by_url(wiki).get()

        context = {'article':article,'create_url':self.create_url}
        if self.request.user.has_perm('wiki.change_article'):
            context['form'] = ArticleForm(instance=article)

        if article.is_redirect and self.request.GET.get('redirect') != 'no':
            return redirect(article.get_redirect_url())
        elif article.slug != wiki.slug or article.namespace != wiki.namespace:
            return redirect(article.get_absolute_url())
        elif article.is_nsfw and not self.show_nsfw_content:
            return render(request, self.nsfw_template, context=context)
        else:
            return render(request, self.article_template, context=context)


class WikiUpdateView(UpdateView):
    model = Article
    fields = ('title','namespace','slug','markdown','is_published','is_nsfw','is_spoiler')
    slug_url_kwarg = 'wiki'
    slug_field = 'wikipath'

class WikiCreateView(CreateView):
    model = Article
    fields = ('title','namespace','slug','markdown','is_published','is_nsfw','is_spoiler')

class WikiEditView(View):
    def get(self, request, wiki):
        article = self._get_article(wiki)
        form = self._get_form(article)
        return render(request, 'wiki/edit.html', context={'form':form,'article':article})

    def post(self, request, wiki):
        article = self._get_article(wiki)
        form = self._get_form(article, request.POST)

        if form.is_valid():
            article = form.save()
            return redirect(article.get_absolute_url())
        else:
            return render(request, 'wiki/edit.html', context={'form':form,'article':article})

    def _get_article(self, wiki):
        try:
            return Article.objects.by_url(wiki).get()
        except Article.DoesNotExist:
            return Article(slug=wiki.slug, namespace=wiki.namespace, title=self._get_title_from_slug(wiki.slug))

    def _get_title_from_slug(self, slug):
        return slug.replace('_', ' ').title()

    def _get_form(self, article, data=None):
        return ArticleForm(data, instance=article)

class PreviewView(View):
    def post(self, request):
        return HttpResponse(markdown_to_html(request.POST.get('markdown', '')))

