import re


from django import forms
from django.core.validators import RegexValidator
from django.db import models


slug_re = r'^[-a-zA-Z0-9_()]+$'
validate_slug = RegexValidator(
    re.compile(slug_re),
    'Please enter a valid slug consisting of letters, numbers, underscores, or hyphens',
    'invalid',
)

namespace_re = r'^(?:[-a-zA-Z0-9_][-a-zA-Z0-9_/]*)?[-a-zA-Z0-9_]$'
validate_namespace = RegexValidator(
    re.compile(namespace_re),
    'Please enter a valid namespace using only letters, numbers, underscores, or hyphens. Separate subnamespaces with a slash (/).',
    'invalid',
)


class WikiSlugFormField(forms.SlugField):
    default_validators = [validate_slug,]


class WikiSlugField(models.SlugField):
    validators = [validate_slug,]

    def formfield(self, **kwargs):
        return super().formfield(form_class=WikiSlugFormField, **kwargs)


class WikiNamespaceFormField(forms.CharField):
    default_validators = [validate_namespace,]


class WikiNamespaceField(models.CharField):
    validators = [validate_namespace,]

    def __init__(self, **kwargs):
        kwargs['max_length'] = 128
        return super().__init__(**kwargs)

    def formfield(self, **kwargs):
        return super().formfield(form_class=WikiNamespaceFormField, **kwargs)


