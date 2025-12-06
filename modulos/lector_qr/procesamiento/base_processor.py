"""Clase base para procesadores de archivos."""

from ..utils import generar_ruta_unica


class BaseProcessor:
    """Clase base para todos los procesadores de archivos."""
    
    def __init__(self, stats, logger, stop_requested_ref, politica_duplicados="renombrar", callback_pregunta=None):
        """
        Args:
            stats: Diccionario de estadísticas compartido
            logger: Función de logging
            stop_requested_ref: Referencia al flag de detención
            politica_duplicados: "renombrar", "preguntar", o "comparar"
            callback_pregunta: Callback para diálogo de duplicados
        """
        self.stats = stats
        self.logger = logger
        self.stop_requested_ref = stop_requested_ref
        self.politica_duplicados = politica_duplicados
        self.callback_pregunta = callback_pregunta
    
    @property
    def stop_requested(self):
        """Obtiene el estado de detención."""
        return self.stop_requested_ref[0] if isinstance(self.stop_requested_ref, list) else self.stop_requested_ref
    
    def log(self, message, level="INFO"):
        """Realiza logging de mensajes."""
        if self.logger:
            self.logger(message, level)
    
    def _obtener_ruta_unica(self, carpeta, nombre_archivo, archivo_origen=None):
        """
        Genera una ruta única para un archivo con manejo avanzado de duplicados.
        
        Args:
            carpeta: Carpeta destino
            nombre_archivo: Nombre del archivo
            archivo_origen: Ruta del archivo origen (para comparar contenido)
            
        Returns:
            tuple: (ruta, accion) - ruta puede ser None si se debe saltar
        """
        return generar_ruta_unica(
            carpeta, nombre_archivo, archivo_origen,
            self.stats, self.log,
            self.politica_duplicados, self.callback_pregunta
        )
