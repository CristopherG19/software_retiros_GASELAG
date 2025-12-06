"""Motor principal para procesamiento de archivos con códigos QR.

Este módulo orquesta el procesamiento de PDFs e imágenes, delegando
la lógica específica a procesadores especializados.
"""

import os
import logging
from .procesamiento import PDFProcessor, ImageProcessor


class MotorQR:
    """Motor principal para el procesamiento de archivos con códigos QR."""
    
    def __init__(self, logger_callback=None, politica_duplicados="renombrar", 
                 callback_pregunta=None):
        """
        Inicializa el motor QR.
        
        Args:
            logger_callback: Función para logging (opcional)
            politica_duplicados: "renombrar", "preguntar", o "comparar"
            callback_pregunta: Callback para diálogo de duplicados (solo si politica=="preguntar")
        """
        self.logger = logging.getLogger("QRMaster")
        self.stop_requested = False
        self.stats = {
            "procesados": 0,
            "exitosos": 0,
            "fallidos": 0,
            "duplicados": 0,
            "saltados": 0
        }
        self.callback = logger_callback
        self.politica_duplicados = politica_duplicados
        self.callback_pregunta = callback_pregunta
        
        # Crear procesadores con política de duplicados
        self.stop_requested_ref = [False]
        self.pdf_processor = PDFProcessor(
            self.stats, self.log, self.stop_requested_ref,
            politica_duplicados, callback_pregunta
        )
        self.image_processor = ImageProcessor(
            self.stats, self.log, self.stop_requested_ref,
            politica_duplicados, callback_pregunta
        )

    def log(self, message, level="INFO"):
        """
        Registra un mensaje.
        
        Args:
            message: Mensaje a registrar
            level: Nivel del mensaje (INFO, SUCCESS, WARNING, ERROR)
        """
        if self.callback:
            self.callback(message, level)
        else:
            print(f"[{level}] {message}")

    def detener(self):
        """Solicita la detención del procesamiento."""
        self.stop_requested = True
        self.stop_requested_ref[0] = True

    def procesar_directorio(self, carpeta_entrada, carpeta_salida, carpeta_error, poppler_path, progress_callback=None):
        """
        Procesa un directorio completo de archivos.
        
        Args:
            carpeta_entrada: Carpeta con archivos a procesar
            carpeta_salida: Carpeta para archivos procesados exitosamente
            carpeta_error: Carpeta para archivos sin QR
            poppler_path: Ruta a Poppler para conversión PDF
            progress_callback: Callback para progreso (opcional)
            
        Returns:
            dict: Estadísticas del procesamiento
        """
        self.stop_requested = False
        self.stop_requested_ref[0] = False
        self.stats = {"procesados": 0, "exitosos": 0, "fallidos": 0, "duplicados": 0, "saltados": 0}
        
        # Actualizar stats reference en procesadores
        self.pdf_processor.stats = self.stats
        self.image_processor.stats = self.stats
        
        # Crear carpetas de salida
        for carpeta in [carpeta_salida, carpeta_error]:
            os.makedirs(carpeta, exist_ok=True)

        # Obtener lista de archivos
        archivos = [f for f in os.listdir(carpeta_entrada) 
                   if os.path.isfile(os.path.join(carpeta_entrada, f))]
        
        if not archivos:
            self.log("No hay archivos para procesar", "WARNING")
            return self.stats

        total = len(archivos)
        self.log(f"Iniciando procesamiento de {total} archivos", "INFO")

        # Procesar cada archivo
        for idx, archivo in enumerate(archivos, 1):
            if self.stop_requested:
                self.log("Procesamiento detenido", "WARNING")
                break

            ruta_original = os.path.join(carpeta_entrada, archivo)
            extension = os.path.splitext(archivo)[1].lower()
            
            # Callback de progreso
            if progress_callback:
                progress_callback(idx, total, archivo)

            try:
                if extension == '.pdf':
                    self.pdf_processor.procesar(ruta_original, carpeta_salida, carpeta_error, poppler_path)
                elif extension in ('.png', '.jpg', '.jpeg', '.tiff', '.bmp'):
                    self.image_processor.procesar(ruta_original, carpeta_salida, carpeta_error)
                else:
                    self.log(f"Ignorado: {archivo} (extensión no soportada)", "WARNING")
            except Exception as e:
                self.log(f"Error en {archivo}: {str(e)}", "ERROR")
                self.stats["fallidos"] += 1

        self.log("Proceso finalizado", "SUCCESS")
        return self.stats
