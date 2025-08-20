from django.db import models

from hub.models import Project

class Repo(models.Model):
    name = models.CharField(max_length=30)
    path = models.CharField(max_length=30)
    description = models.CharField(max_length=50)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
