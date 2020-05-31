from django.conf import settings
from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'6', settings.ROOT_URLCONF, name='6'),
    host(r'5', 'archives.ugahacks5_urls', name='5'),
    host(r'blog', 'blog.urls', name='blog'),
)
