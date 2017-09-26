from django.http import Http404
from django.shortcuts import get_object_or_404,redirect,render
from django.utils.safestring import mark_safe
from django.views import View
from django.views.generic import DetailView,ListView
from django.views.generic.base import TemplateView


from .models import Article,Tag,RedirectPage


# Create your views here.

class TagView(TemplateView):
    model = Tag
    context_object_name = 'tag'
    template_name = 'wiki/article_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        tag = get_object_or_404(Tag, slug=self.kwargs['slug'])

        context['articles'] = tag.articles.order_by('slug')
        context['title'] = 'Articles tagged "{name}"'.format(name=tag.name)
        context['description'] = tag.html

        return context


class ArticleListView(ListView):
    queryset = Article.objects.filter(is_published=True).exclude(slug__startswith='special:').order_by('slug')
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

        article = qs.get(slug__iexact=slug)

        if article.slug != slug:
            return redirect(article.get_absolute_url())
        elif article.is_nsfw and not self.show_nsfw_content:
            return render(request, self.nsfw_template, context={'article':article})
        else:
            return render(request, self.article_template, context={'article':article})

    def get_redirect(self, request, slug):
        qs = RedirectPage.objects.filter(slug__iexact=slug)

        try:
            return redirect(qs.get().article.get_absolute_url())
        except RedirectPage.MultipleObjectsReturned:
            rp = qs.first()

            if rp.slug != slug:
                return redirect('wiki', slug=rp.slug)
            else:
                context = {
                        'articles': Article.objects.filter(redirectpage__slug__iexact=slug).order_by('slug'),
                        'title': '{slug} (Disambiguation)'.format(slug=slug),
                        'description': mark_safe('<p><strong>{slug}</strong> may refer to:</p>'.format(slug=slug)),
                        }
                return render(request, self.disambiguation_template, context=context)

