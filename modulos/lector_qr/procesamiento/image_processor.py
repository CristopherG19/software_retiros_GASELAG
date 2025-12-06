"""Procesador de archivos de imagen."""

import os
import shutil
from PIL import Image
from .base_processor import BaseProcessor


class ImageProcessor(BaseProcessor):
    """Procesador especializado para archivos de imagen."""
    
    def procesar(self, ruta_img, salida, error):
        """
        Procesa un archivo de imagen.
        
        Args:
            ruta_img: Ruta de la imagen a procesar
            salida: Carpeta para archivos exitosos
            error: Carpeta para archivos sin QR
        """
        try:
            imagen = Image.open(ruta_img)
            
            from ..utils import leer_qr
            texto_qr = leer_qr(imagen)
            self.stats["procesados"] += 1
            
            ext = os.path.splitext(ruta_img)[1]
            
            if texto_qr:
                nombre_limpio = "".join([c for c in texto_qr if c.isalnum() or c in " -_"])
                nuevo_nombre = f"{nombre_limpio}{ext}"
                ruta_final, accion = self._obtener_ruta_unica(salida, nuevo_nombre, ruta_img)
                
                if ruta_final is None:
                    self.stats["saltados"] += 1
                    return
                
                shutil.copy2(ruta_img, ruta_final)
                
                if accion == "sobrescrito":
                    self.log(f"  {os.path.basename(ruta_img)} -> [SOBRESCRITO] {os.path.basename(ruta_final)}", "WARNING")
                else:
                    self.log(f"  {os.path.basename(ruta_img)} -> {os.path.basename(ruta_final)}", "SUCCESS")
                
                self.stats["exitosos"] += 1
            else:
                ruta_final, accion = self._obtener_ruta_unica(error, os.path.basename(ruta_img), ruta_img)
                
                if ruta_final is None:
                    self.stats["saltados"] += 1
                    return
                
                shutil.copy2(ruta_img, ruta_final)
                self.log(f"  {os.path.basename(ruta_img)} -> Sin QR", "ERROR")
                self.stats["fallidos"] += 1
                
        except Exception as e:
            self.log(f"Error en imagen {os.path.basename(ruta_img)}: {e}", "ERROR")
