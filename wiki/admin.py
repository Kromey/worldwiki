from django.contrib import admin


from . import models


# Register your models here.

class PageAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.Page, PageAdmin)
