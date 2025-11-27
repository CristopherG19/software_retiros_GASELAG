import os
import shutil
from pyzbar.pyzbar import decode
from PIL import Image
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
import logging

class MotorQR:
    def __init__(self, logger_callback=None):
        self.logger = logging.getLogger("QRMaster")
        self.stop_requested = False
        self.stats = {
            "procesados": 0,
            "exitosos": 0,
            "fallidos": 0
        }
        self.callback = logger_callback

    def log(self, message, level="INFO"):
        if self.callback:
            self.callback(message, level)
        else:
            print(f"[{level}] {message}")

    def detener(self):
        self.stop_requested = True

    def procesar_directorio(self, carpeta_entrada, carpeta_salida, carpeta_error, poppler_path, progress_callback=None):
        self.stop_requested = False
        self.stats = {"procesados": 0, "exitosos": 0, "fallidos": 0}
        
        # Crear carpetas
        for carpeta in [carpeta_salida, carpeta_error]:
            os.makedirs(carpeta, exist_ok=True)

        archivos = [f for f in os.listdir(carpeta_entrada) 
                   if os.path.isfile(os.path.join(carpeta_entrada, f))]
        
        if not archivos:
            self.log("No hay archivos para procesar", "WARNING")
            return self.stats

        total = len(archivos)
        self.log(f"Iniciando procesamiento de {total} archivos", "INFO")

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
                    self._procesar_pdf(ruta_original, carpeta_salida, carpeta_error, poppler_path)
                elif extension in ('.png', '.jpg', '.jpeg', '.tiff', '.bmp'):
                    self._procesar_imagen(ruta_original, carpeta_salida, carpeta_error)
                else:
                    self.log(f"Ignorado: {archivo} (extensión no soportada)", "WARNING")
            except Exception as e:
                self.log(f"Error en {archivo}: {str(e)}", "ERROR")
                self.stats["fallidos"] += 1

        self.log("Proceso finalizado", "SUCCESS")
        return self.stats

    def _procesar_pdf(self, ruta_pdf, salida, error, poppler_path):
        try:
            reader = PdfReader(ruta_pdf)
            total_paginas = len(reader.pages)
            
            for num_pagina in range(1, total_paginas + 1):
                if self.stop_requested: break
                
                # Convertir a imagen
                try:
                    kwargs = {'first_page': num_pagina, 'last_page': num_pagina}
                    if os.path.exists(poppler_path):
                        kwargs['poppler_path'] = poppler_path
                    
                    imagenes = convert_from_path(ruta_pdf, **kwargs)
                except Exception as e:
                    self.log(f"  Error convirtiendo pág {num_pagina}: {e}", "ERROR")
                    continue

                if self.stop_requested: break

                if not imagenes: continue
                
                imagen = imagenes[0]
                texto_qr = self._leer_qr(imagen)
                self.stats["procesados"] += 1

                nombre_base = os.path.splitext(os.path.basename(ruta_pdf))[0]
                
                if texto_qr:
                    nombre_limpio = "".join([c for c in texto_qr if c.isalnum() or c in " -_"])
                    nuevo_nombre = f"{nombre_limpio}.pdf"
                    ruta_final = self._generar_ruta_unica(salida, nuevo_nombre)
                    
                    imagen.save(ruta_final, "PDF", resolution=100.0, save_all=True)
                    self.log(f"  Pág {num_pagina} -> {os.path.basename(ruta_final)}", "SUCCESS")
                    self.stats["exitosos"] += 1
                else:
                    nombre_error = f"{nombre_base}_pag{num_pagina}.pdf"
                    ruta_final = self._generar_ruta_unica(error, nombre_error)
                    
                    imagen.save(ruta_final, "PDF", resolution=100.0, save_all=True)
                    self.log(f"  Pág {num_pagina} sin QR -> {os.path.basename(ruta_final)}", "ERROR")
                    self.stats["fallidos"] += 1

        except Exception as e:
            self.log(f"Error crítico en PDF {os.path.basename(ruta_pdf)}: {e}", "ERROR")

    def _procesar_imagen(self, ruta_img, salida, error):
        try:
            imagen = Image.open(ruta_img)
            texto_qr = self._leer_qr(imagen)
            self.stats["procesados"] += 1
            
            ext = os.path.splitext(ruta_img)[1]
            
            if texto_qr:
                nombre_limpio = "".join([c for c in texto_qr if c.isalnum() or c in " -_"])
                nuevo_nombre = f"{nombre_limpio}{ext}"
                ruta_final = self._generar_ruta_unica(salida, nuevo_nombre)
                
                shutil.copy2(ruta_img, ruta_final)
                self.log(f"  {os.path.basename(ruta_img)} -> {os.path.basename(ruta_final)}", "SUCCESS")
                self.stats["exitosos"] += 1
            else:
                ruta_final = self._generar_ruta_unica(error, os.path.basename(ruta_img))
                shutil.copy2(ruta_img, ruta_final)
                self.log(f"  {os.path.basename(ruta_img)} -> Sin QR", "ERROR")
                self.stats["fallidos"] += 1

        except Exception as e:
            self.log(f"Error en imagen {os.path.basename(ruta_img)}: {e}", "ERROR")

    def _leer_qr(self, imagen):
        try:
            codigos = decode(imagen)
            if codigos:
                return codigos[0].data.decode("utf-8")
        except:
            pass
        return None

    def _generar_ruta_unica(self, carpeta, nombre_archivo):
        base, ext = os.path.splitext(nombre_archivo)
        contador = 1
        ruta = os.path.join(carpeta, nombre_archivo)
        while os.path.exists(ruta):
            ruta = os.path.join(carpeta, f"{base}_{contador}{ext}")
            contador += 1
        return ruta
