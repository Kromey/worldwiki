from django.forms import ModelForm,Textarea


from .models import Article


class ArticleForm(ModelForm):
    class Meta:
        model = Article
        fields = ('title','slug','markdown','is_published','is_nsfw','is_spoiler')
        widgets = {
                'markdown': Textarea(
                    attrs={
                        'data-provide':'markdown',
                        'data-resize': 'vertical',
                        }),
                }

