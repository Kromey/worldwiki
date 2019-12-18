from django.contrib import admin


from . import models


# Register your models here.

class TagAdmin(admin.ModelAdmin):
    list_display = (
            'name',
            'slug',
            )
    fields = (
            'name',
            'slug',
            'description',
            )


class ArticleAdmin(admin.ModelAdmin):
    fields = (
            'title',
            (
                'namespace',
                'slug',
            ),
            (
                'published',
                'edited',
            ),
            (
                'is_published',
                'is_nsfw',
                'is_spoiler',
            ),
            'markdown',
            'tags',
            )
    list_display = (
            'title',
            'view_link',
            'published',
            'edited',
            'is_redirect',
            'is_published',
            'is_nsfw',
            'is_spoiler',
            )
    readonly_fields = ('published','edited')
    filter_horizontal = ('tags',)

    def is_redirect(self, obj):
        return obj.is_redirect
    is_redirect.short_description = 'redirect?'
    is_redirect.boolean = True

admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.Article, ArticleAdmin)

