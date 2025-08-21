from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings

from .models import Repo

import os
import pygit2

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from pygments.lexers import guess_lexer_for_filename
from pygments.styles import get_style_by_name

def get_repo(name):
    repo_obj = Repo.objects.get( name = name )
    return pygit2.Repository(os.path.expandvars(os.path.expanduser(os.path.join(settings.REPOS_PATH, repo_obj.path))))

def get_file(repo, ref, path):
    commit = repo.revparse_single(ref)
    path = os.path.normpath(path)
    sub = path.split('/')
    obj = commit.tree
    if sub[0] == '.':
        return obj
    for path in sub:
        obj = obj[path]
    return obj

def index(request):
    return render(request, 'git/index.html', {})

def repo(request, name):
    repo = get_repo(name)
    index = repo.index

    return render(request, 'git/repository.html', {})

def tree_file(request, repo, ref, path):
    repo = get_repo(repo)
    index = repo.index
    index.read()

    obj = get_file(repo, ref, path)

    if not isinstance(obj, pygit2.Blob):
        return tree_dir(obj)

    content = obj.data
    line_count = len(obj.data.splitlines())
    try:
        lexer = guess_lexer_for_filename(path, "")
    except Exception:
        from pygments.lexers import TextLexer
        lexer = TextLexer()
    formatter = HtmlFormatter(cssclass = 'source', wrapcode = True, linespans = 'line', style='monokai')

    css = formatter.get_style_defs('.source')
    print(css)
    return render(request, 'git/file.html', {'content': highlight(content, lexer, formatter), 'lines': range(1, line_count+1), 'pygments_css': css})

def tree_dir(obj):
    return HttpResponse("dir")

def diff(request, repo):
    repo = get_repo(repo)
    first = request.GET.get('first')
    second = request.GET.get('second')

    old_commit = repo.revparse_single(first)
    new_commit = repo.revparse_single(second)

    diff = repo.diff(old_commit.tree, new_commit.tree)
    formatter = HtmlFormatter(style="monokai", nowrap=True, noclasses=True)
    files = []

    for patch in diff:
        lexer = guess_lexer_for_filename(patch.delta.new_file.path, "")
        try:
            lexer = guess_lexer_for_filename(patch.delta.new_file.path, "")
        except Exception:
            from pygments.lexers import TextLexer
            lexer = TextLexer()

        file_diff = {
            "old_path": patch.delta.old_file.path,
            "new_path": patch.delta.new_file.path,
            "hunks": []
        }

        for hunk in patch.hunks:
            hunk_lines = []
            for line in hunk.lines:
                hunk_lines.append({
                    "origin": line.origin,
                    "old_lineno": line.old_lineno,
                    "new_lineno": line.new_lineno,
                    "content": highlight(line.content, lexer, formatter)
                })
            file_diff["hunks"].append({
                "header": f"@@ -{hunk.old_start},{hunk.old_lines} +{hunk.new_start},{hunk.new_lines} @@",
                "lines": hunk_lines
            })

        files.append(file_diff)

    return render(request, "git/diff.html", {"files": files})
