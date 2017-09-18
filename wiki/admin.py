from django.contrib import admin


from . import models


# Register your models here.

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
                'is_nsfw',
                'is_spoiler',
            ),
            'markdown',
            )
    list_display = (
            'title',
            'published',
            'edited',
            'is_nsfw',
            'is_spoiler',
            )
    readonly_fields = ('published','edited')

admin.site.register(models.Article, ArticleAdmin)
