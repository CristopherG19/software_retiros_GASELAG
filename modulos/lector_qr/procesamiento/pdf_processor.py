"""Procesador de archivos PDF."""

import os
import shutil
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
from .base_processor import BaseProcessor


class PDFProcessor(BaseProcessor):
    """Procesador especializado para archivos PDF."""
    
    def procesar(self, ruta_pdf, salida, error, poppler_path):
        """
        Procesa un archivo PDF.
        
        Args:
            ruta_pdf: Ruta del PDF a procesar
            salida: Carpeta para archivos exitosos
            error: Carpeta para archivos sin QR
            poppler_path: Ruta a Poppler para conversión PDF
        """
        try:
            reader = PdfReader(ruta_pdf)
            total_paginas = len(reader.pages)
            
            # PDFs de 1 página: preservar calidad
            if total_paginas == 1:
                self._procesar_pdf_simple(ruta_pdf, salida, error, poppler_path)
            else:
                # PDFs multipágina: procesar página por página
                self._procesar_pdf_multipagina(ruta_pdf, salida, error, poppler_path)
                
        except Exception as e:
            self.log(f"Error crítico en PDF {os.path.basename(ruta_pdf)}: {e}", "ERROR")
    
    def _procesar_pdf_simple(self, ruta_pdf, salida, error, poppler_path):
        """Procesa un PDF de una sola página preservando calidad."""
        try:
            kwargs = {}
            if os.path.exists(poppler_path):
                kwargs['poppler_path'] = poppler_path
            
            imagenes = convert_from_path(ruta_pdf, **kwargs)
        except Exception as e:
            self.log(f"  Error convirtiendo PDF: {e}", "ERROR")
            return

        if not imagenes:
            self.log(f"  No se pudo convertir el PDF a imagen", "ERROR")
            return
        
        # Leer QR de la imagen temporal
        from ..utils import leer_qr
        imagen = imagenes[0]
        texto_qr = leer_qr(imagen)
        self.stats["procesados"] += 1

        if texto_qr:
            nombre_limpio = "".join([c for c in texto_qr if c.isalnum() or c in " -_"])
            nuevo_nombre = f"{nombre_limpio}.pdf"
            ruta_final, accion = self._obtener_ruta_unica(salida, nuevo_nombre, ruta_pdf)
            
            # Si es None, saltar archivo
            if ruta_final is None:
                self.stats["saltados"] += 1
                return
            
            # COPIAR EL PDF ORIGINAL (preserva calidad)
            shutil.copy2(ruta_pdf, ruta_final)
            
            # Log diferenciado según acción
            if accion == "sobrescrito":
                self.log(f"  {os.path.basename(ruta_pdf)} -> [SOBRESCRITO] {os.path.basename(ruta_final)}", "WARNING")
            else:
                self.log(f"  {os.path.basename(ruta_pdf)} -> {os.path.basename(ruta_final)}", "SUCCESS")
            
            self.stats["exitosos"] += 1
        else:
            ruta_final, accion = self._obtener_ruta_unica(error, os.path.basename(ruta_pdf), ruta_pdf)
            
            if ruta_final is None:
                self.stats["saltados"] += 1
                return
                
            shutil.copy2(ruta_pdf, ruta_final)
            self.log(f"  {os.path.basename(ruta_pdf)} -> Sin QR", "ERROR")
            self.stats["fallidos"] += 1
    
    def _procesar_pdf_multipagina(self, ruta_pdf, salida, error, poppler_path):
        """Procesa un PDF multipágina separando por páginas."""
        try:
            reader = PdfReader(ruta_pdf)
            total_paginas = len(reader.pages)
            
            for num_pagina in range(1, total_paginas + 1):
                if self.stop_requested:
                    break
                
                # Convertir página específica a imagen
                try:
                    kwargs = {'first_page': num_pagina, 'last_page': num_pagina}
                    if os.path.exists(poppler_path):
                        kwargs['poppler_path'] = poppler_path
                    
                    imagenes = convert_from_path(ruta_pdf, **kwargs)
                except Exception as e:
                    self.log(f"  Error convirtiendo pág {num_pagina}: {e}", "ERROR")
                    continue

                if self.stop_requested or not imagenes:
                    break
                
                from ..utils import leer_qr
                imagen = imagenes[0]
                texto_qr = leer_qr(imagen)
                self.stats["procesados"] += 1

                nombre_base = os.path.splitext(os.path.basename(ruta_pdf))[0]
                
                if texto_qr:
                    nombre_limpio = "".join([c for c in texto_qr if c.isalnum() or c in " -_"])
                    nuevo_nombre = f"{nombre_limpio}.pdf"
                    # Para multipágina no comparamos contenido (son imágenes convertidas)
                    ruta_final, accion = self._obtener_ruta_unica(salida, nuevo_nombre)
                    
                    if ruta_final is None:
                        self.stats["saltados"] += 1
                        continue
                    
                    # Para multipágina, guardar imagen convertida
                    imagen.save(ruta_final, "PDF", resolution=100.0, save_all=True)
                    
                    if accion == "sobrescrito":
                        self.log(f"  Pág {num_pagina} -> [SOBRESCRITO] {os.path.basename(ruta_final)}", "WARNING")
                    else:
                        self.log(f"  Pág {num_pagina} -> {os.path.basename(ruta_final)}", "SUCCESS")
                    
                    self.stats["exitosos"] += 1
                else:
                    nombre_error = f"{nombre_base}_pag{num_pagina}.pdf"
                    ruta_final, accion = self._obtener_ruta_unica(error, nombre_error)
                    
                    if ruta_final is None:
                        self.stats["saltados"] += 1
                        continue
                    
                    imagen.save(ruta_final, "PDF", resolution=100.0, save_all=True)
                    self.log(f"  Pág {num_pagina} sin QR -> {os.path.basename(ruta_final)}", "ERROR")
                    self.stats["fallidos"] += 1
                    
        except Exception as e:
            self.log(f"Error en PDF multipágina: {e}", "ERROR")
