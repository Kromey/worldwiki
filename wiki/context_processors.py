from .models import Article


def wiki_sidebar(request):
    try:
        sidebar = Article.objects.get(slug='sidebar')
        return {
                'sidebar_content': sidebar.html,
                'sidebar_class': 'sidebar col-md-3',
                'content_class': 'content col-md-9',
                }
    except Article.DoesNotExist:
        return {
                'sidebar_content': 'To display a sidebar, create an article with the slug "sidebar"',
                'sidebar_class': 'sidebar hidden',
                'content_class': 'content col-md-12',
                }

