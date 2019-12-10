from django.conf import settings


from .models import Article


class WikiSidebar:
    SLUG = 'sidebar'
    def __init__(self):
        try:
            sidebar = Article.objects.get(slug=WikiSidebar.SLUG)

            self.content = sidebar.html
            self.css = 'sidebar col-md-3'
            self.exists = True
        except Article.DoesNotExist:
            self.content = 'To display a sidebar, create an article with the slug "{slug}"'.format(slug=WikiSidebar.SLUG)
            self.css = 'sidebar hidden'
            self.exists = False

def wiki(request):
    sidebar = WikiSidebar()

    content_css = 'content col-md-{}'.format('9' if sidebar.exists else '12')

    try:
        title = settings.WIKI['title']
    except (AttributeError,KeyError):
        title = None

    return {
        'wiki': {
            'sidebar': sidebar,
            'css': content_css,
            'title': title,
        }
    }

