from django.http import Http404,HttpResponse
from django.shortcuts import get_object_or_404,redirect,render
from django.urls import reverse,reverse_lazy
from django.utils.safestring import mark_safe
from django.views import View
from django.views.generic import DetailView,ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView,UpdateView


from wiki import utils
from wiki.markdown import markdown_to_html
from wiki.models import Article,Tag,Term
from wiki.pages import Error404


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

    def get(self, request, slug, namespace):
        self.show_nsfw_content = self.show_nsfw_content or request.session.get('show_nsfw', False)

        redirected, article = self.get_article(slug, namespace)
        context = {
            'article':article,
            'redirected':redirected,
        }

        if article.is_nsfw and not self.show_nsfw_content:
            return render(request, self.nsfw_template, context=context)
        else:
            return render(request, self.article_template, context=context)

    def post(self, request, *args, **kwargs):
        if request.POST.get('show-me'):
            self.show_nsfw_content = True
            if request.POST.get('remember'):
                request.session['show_nsfw'] = True

        return self.get(request, *args, **kwargs)

    def get_article(self, slug, namespace):
        if self.request.user.has_perm('wiki.change_article') or 'preview' in self.request.GET:
            qs = Article.objects
        else:
            qs = Article.objects.filter(is_published=True)

        try:
            article = qs.get(slug=slug, namespace=namespace)
        except Article.DoesNotExist:
            return self.get_404(request, slug, namespace)

        if article.is_redirect and self.request.GET.get('redirect') != 'no':
            try:
                return (article, article.get_redirect(qs))
            except Article.DoesNotExist:
                pass

        return (None, article)

    def get_404(self, request, slug, namespace):
        context = {
            'article': Error404.get(),
            'create_url': reverse('wiki-new', args=[namespace, slug]),
        }

        return render(request, self.article_template, context=context)


class WikiUpdateView(UpdateView):
    model = Article
    fields = ('title','markdown','is_published','is_nsfw','is_spoiler')

    def get_object(self, queryset=None):
        queryset = queryset or self.get_queryset()

        return queryset.get(**self.kwargs)

class WikiCreateView(CreateView):
    model = Article
    fields = ('title','namespace','slug','markdown','is_published','is_nsfw','is_spoiler')

    def get_initial(self):
        slug = self.kwargs['slug']
        title = slug.replace('_', ' ').strip().title()

        if not self.kwargs['slug'].startswith('_'):
            slug = utils.slugify(title)

        initial = {
            'title': title,
            'slug': slug,
            'namespace': self.kwargs['namespace'],
            'is_published': True,
        }

        template = self._get_template()
        if template:
            initial['markdown'] = template

        return initial

    def _get_template(self):
        # Start with a bogus "extra" namespace
        # We'll pop it off before the first lookup, which is how we'll get to the root
        namespace = utils.join_path(self.kwargs['namespace'], '__extra__')

        while namespace:
            namespace = utils.namespace(namespace)

            try:
                tmpl = Article.objects.get(namespace=namespace, slug='_template')
                return tmpl.markdown
            except Article.DoesNotExist:
                pass

        return None

class PreviewView(View):
    def post(self, request):
        return HttpResponse(markdown_to_html(request.POST.get('markdown', '')))


class GlossaryView(ListView):
    model = Term
    context_object_name = 'terms'

class TermCreateView(CreateView):
    model = Term
    fields = ('term', 'definition')

class TermEditView(UpdateView):
    model = Term
    fields = ('term', 'definition')


