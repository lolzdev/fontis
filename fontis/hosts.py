from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'git', 'git.urls', name='git'),
    host(r'builds', 'builds.urls', name='builds'),
)
