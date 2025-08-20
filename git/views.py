from django.shortcuts import render
from django.shortcuts import render
from django.http import HttpResponse

from .models import Repo

from django.conf import settings

import os

import pygit2

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.styles import get_style_by_name

def get_repo(name):
    repo_obj = Repo.objects.get( name = name )
    return pygit2.Repository(os.path.expandvars(os.path.expanduser(os.path.join(settings.REPOS_PATH, repo_obj.path))))

def walk_repo_files(repo, branch):
    tree = repo.revparse_single(branch).tree
    trees_and_paths = [(tree, [])]
    while len(trees_and_paths) != 0:
        tree, path = trees_and_paths.pop() # take the last entry
        for entry in tree:
            if entry.filemode == pygit2.GIT_FILEMODE_TREE:
                next_tree = repo.get(entry.id)
                next_path = list(path)
                next_path.append(entry.name)
                trees_and_paths.append((next_tree, next_path,))
            else:
                yield os.path.join(*path, entry.name)

def index(request):
    return render(request, 'git/index.html', {})

def repo(request, name):
    repo = get_repo(name)
    index = repo.index
    #messages = [repo[index[m].id].data for m in walk_repo_files(repo, "master")]

    return render(request, 'git/repository.html', {})

def tree_file(request, repo, path):
    repo = get_repo(repo)
    index = repo.index
    index.read()
    content = repo[index[path].id].data
    line_count = len(repo[index[path].id].data.splitlines())
    lexer = get_lexer_by_name("zig", stripall=True)
    formatter = HtmlFormatter(lineos=True, cssclass="source");

    return render(request, 'git/file.html', {'content': highlight(content, lexer, formatter), 'lines': '\n'.join(map(str, range(1, line_count+1)))})
