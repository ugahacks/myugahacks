from django.conf import settings
from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'my', settings.ROOT_URLCONF, name='my'),  # <-- The `name` we used to in the `DEFAULT_HOST` setting
    host(r'5', 'archives.ugahacks5_urls', name='5'),  # <-- The `name` we used to in the `DEFAULT_HOST` setting
)
