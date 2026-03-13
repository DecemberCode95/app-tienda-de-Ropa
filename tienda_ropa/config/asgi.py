"""
ASGI config for tienda_ropa project.

Expone la aplicación ASGI llamada `application` que será usada por
servidores ASGI como Uvicorn o Daphne para soporte de WebSockets y async.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_asgi_application()
