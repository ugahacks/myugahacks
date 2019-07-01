import os
import sys
path = '/home/ugahacks/ugahacks5'
if path not in sys.path:
    sys.path.append(path)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("home/ugahacks/ugahacks5/config/settings/local.py")

application = get_wsgi_application()
