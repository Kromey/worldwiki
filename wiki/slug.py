from django import forms
from django.db import models


from wiki.path import WikiPath


class WikiSlugFormField(forms.SlugField):
    default_validators = [WikiPath.validate_slug,]

class WikiSlugField(models.SlugField):
    validators = [WikiPath.validate_slug,]

    def formfield(self, **kwargs):
        return super().formfield(form_class=WikiSlugFormField, **kwargs)


class WikiNamespaceFormField(forms.CharField):
    default_validators = [WikiPath.validate_namespace,]

class WikiNamespaceField(models.CharField):
    validators = [WikiPath.validate_namespace,]

    def __init__(self, **kwargs):
        kwargs['max_length'] = 128
        return super().__init__(**kwargs)

    def formfield(self, **kwargs):
        return super().formfield(form_class=WikiNamespaceFormField, **kwargs)


