import os
from django.core.wsgi import get_wsgi_application

# Onde estiver:
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'config.settings_pythonanywhere')

application = get_wsgi_application()
