import os
from django.core.asgi import get_asgi_application

# Onde estiver:
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'loja.settings')

application = get_asgi_application()
