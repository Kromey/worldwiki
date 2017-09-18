def wiki_sidebar(request):
    return {
            'sidebar_content': 'This is the sidebar',
            'sidebar_class': 'sidebar col-md-3',
            'content_class': 'content col-md-9',
            }
