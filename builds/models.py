from django.db import models
import uuid

from git.models import Repo

class Script(models.Model):
    class Trigger(models.TextChoices):
        PUSH = 'PS', ("Push")
        PATCH = 'PT', ("Patch")

    name = models.CharField(max_length=30)
    image = models.CharField(max_length=30)
    bash = models.TextField()
    trigger = models.CharField(max_length=2, choices=Trigger.choices, default=Trigger.PUSH)
    repository = models.ForeignKey(Repo, on_delete=models.CASCADE)

class ScriptResult(models.Model):
    class Status(models.TextChoices):
        SUCCESS = 'SC', ("Success")
        FAILED = 'FL', ("Failed")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    commit = models.CharField(max_length=30)
    branch = models.CharField(max_length=30)
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.FAILED)
    script = models.ForeignKey(Script, on_delete=models.CASCADE)
