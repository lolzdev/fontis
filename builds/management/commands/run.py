from django.core.management.base import BaseCommand, CommandError
from podman import PodmanClient
from django.conf import settings

from builds.models import ScriptResult, Script
from git.models import Repo

import pygit2
import os

class Command(BaseCommand):
    help = "Run a script"

    def add_arguments(self, parser):
        parser.add_argument("repo", type=str)
        parser.add_argument("script", type=str)
        parser.add_argument("branch", type=str)
        parser.add_argument("commit", type=str)

    def handle(self, *args, **options):
        repo_obj = Repo.objects.get( name = options["repo"] )
        repo = pygit2.Repository(os.path.expandvars(os.path.expanduser(os.path.join(settings.REPOS_PATH, repo_obj.path))))

        script = Script.objects.get( repository = repo_obj, name = options["script"] )

        result = ScriptResult(commit = options["commit"], branch = options["branch"], status = "RN", script = script)
        result.save()

        with PodmanClient(base_url=settings.PODMAN_URL) as client:

            client.images.pull(script.image)
            container = client.containers.create(
                script.image,
                command = ["sh", "-c", script.bash],
                auto_remove = True,
                stdout = True,
                stderr = True,
            )
            container.start()
            exit_code = container.wait()
            status = "SC"
            if exit_code != 0:
                status = "FL"

            result.status = status;
            result.save()

            logs = "".join(chunk.decode() for chunk in container.logs(stdout=True, stderr=True))
            with open(os.path.expandvars(os.path.expanduser(os.path.join(settings.CI_LOGS_PATH, str(result.id)))), "w", encoding="utf-8") as f:
                f.write(logs)
                f.close()
            
