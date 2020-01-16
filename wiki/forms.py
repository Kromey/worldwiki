from django.forms import ModelForm,CharField


from wiki.models import Article,Tag


class TaggableArticleMixin(ModelForm):
    tag_list = CharField(
        required=False,
        max_length=1024,
        label='Tags',
        help_text='Multiple tags may be separated by commas',
    )

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            tags = ','.join([tag.name for tag in instance.tags.all()])
            if tags:
                initial = kwargs.get('initial', {})
                initial['tag_list'] = tags
                kwargs['initial'] = initial

        return super().__init__(*args, **kwargs)

    def _save_tags(self):
        tags = self.cleaned_data['tag_list'].split(',')
        objs = []

        for tag in tags:
            tag = tag.strip()
            if not tag:
                continue

            obj, created = Tag.objects.get_or_create(
                name__iexact=tag,
                defaults={'name':tag},
            )
            objs.append(obj)

        if objs:
            self.instance.tags.set(objs)

    def save(self, commit=True):
        # TODO: If commit is True, postpone saving tags until save_m2m() called
        # In the meantime, that function is not implemented
        raise NotImplementedError()

        obj = super().save(commit)

        self._save_tags()

        return obj


class ArticleCreateForm(TaggableArticleMixin, ModelForm):
    class Meta:
        model = Article
        fields = ('title','namespace','slug','tag_list','markdown','is_published','is_nsfw','is_spoiler')


class ArticleUpdateForm(TaggableArticleMixin, ModelForm):
    class Meta:
        model = Article
        fields = ('title','tag_list','markdown','is_published','is_nsfw','is_spoiler')

