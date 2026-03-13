"""
Configuración de la aplicación Tienda.
"""

from django.apps import AppConfig


class TiendaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tienda'
    verbose_name = 'Tienda de Ropa'
    
    def ready(self):
        """
        Método llamado cuando la aplicación está lista.
        Aquí se pueden importar señales u otras configuraciones.
        """
        # Importar señales si es necesario
        # from . import signals
        pass
