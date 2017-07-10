from django.db import models


# Create your models here.

class Page(models.Model):
    path = models.CharField(max_length=255)
    body = models.TextField()

    def __str__(self):
        return '/' + self.path

