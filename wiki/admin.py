from django.contrib import admin


from . import models


# Register your models here.

class ArticleAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(models.Article, ArticleAdmin)
