"""
Configuración WSGI para el proyecto Tienda de Ropa.

Expone la aplicación WSGI llamada `application` que será usada por
servidores como Gunicorn o uWSGI en producción.
"""

import os
from django.core.wsgi import get_wsgi_application

# Configurar variables de entorno
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
