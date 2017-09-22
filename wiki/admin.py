from django.contrib import admin


from . import models


# Register your models here.

class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = (
            'name',
            'slug',
            )
    fields = (
            'name',
            'slug',
            )


class ArticleAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    fields = (
            'title',
            'slug',
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
            'is_published',
            'is_nsfw',
            'is_spoiler',
            )
    readonly_fields = ('published','edited')
    filter_horizontal = ('tags',)

admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.Article, ArticleAdmin)
