from django.db import models

class Repo(models.Model):
    name = models.CharField(max_length=30)
    path = models.CharField(max_length=30)
    description = models.CharField(max_length=50)
