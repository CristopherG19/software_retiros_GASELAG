"""Clase base para procesadores de archivos."""

from ..utils import generar_ruta_unica


class BaseProcessor:
    """Clase base para todos los procesadores de archivos."""
    
    def __init__(self, stats, logger, stop_requested_ref):
        """
        Args:
            stats: Diccionario de estadísticas compartido
            logger: Función de logging
            stop_requested_ref: Referencia al flag de detención
        """
        self.stats = stats
        self.logger = logger
        self.stop_requested_ref = stop_requested_ref
    
    @property
    def stop_requested(self):
        """Obtiene el estado de detención."""
        return self.stop_requested_ref[0] if isinstance(self.stop_requested_ref, list) else self.stop_requested_ref
    
    def log(self, message, level="INFO"):
        """Realiza logging de mensajes."""
        if self.logger:
            self.logger(message, level)
    
    def _obtener_ruta_unica(self, carpeta, nombre_archivo):
        """
        Genera una ruta única para un archivo.
        
        Args:
            carpeta: Carpeta destino
            nombre_archivo: Nombre del archivo
            
        Returns:
            str: Ruta única
        """
        return generar_ruta_unica(carpeta, nombre_archivo, self.stats, self.log)
