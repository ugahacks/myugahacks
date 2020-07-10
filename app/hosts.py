from django.conf import settings
from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'my', settings.ROOT_URLCONF, name='my'),
    host(r'blog', 'blog.urls', name='blog'),
)
