from django.shortcuts import render
from django.http import HttpResponse
from celery import shared_task

from git.models import Repo


def index(request):
    repo_obj = Repo.objects.get( name = "sideros" )
    return HttpResponse(f"{repo_obj.description}")
