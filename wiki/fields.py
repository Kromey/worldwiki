from django import forms
from django.db import models


from wiki import utils


class CILookupMixin:
    def get_lookup(self, lookup_name):
        if lookup_name == 'exact':
            lookup_name = 'iexact'

        return super().get_lookup(lookup_name)


class WikiSlugFormField(forms.SlugField):
    default_validators = [utils.validate_slug,]

class WikiSlugField(CILookupMixin, models.SlugField):
    validators = [utils.validate_slug,]

    def formfield(self, **kwargs):
        return super().formfield(form_class=WikiSlugFormField, **kwargs)


class WikiNamespaceFormField(forms.CharField):
    default_validators = [utils.validate_namespace,]

class WikiNamespaceField(CILookupMixin, models.CharField):
    validators = [utils.validate_namespace,]

    def __init__(self, **kwargs):
        kwargs['max_length'] = 128
        return super().__init__(**kwargs)

    def formfield(self, **kwargs):
        return super().formfield(form_class=WikiNamespaceFormField, **kwargs)


