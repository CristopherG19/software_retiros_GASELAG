"""Utilidades para manejo de archivos y detección de duplicados."""

import os


def generar_ruta_unica(carpeta, nombre_archivo, stats=None, logger=None):
    """
    Genera una ruta única para un archivo, manejando duplicados.
    
    Args:
        carpeta: Carpeta destino
        nombre_archivo: Nombre deseado del archivo
        stats: Diccionario de estadísticas (opcional)
        logger: Función de logging (opcional)
        
    Returns:
        str: Ruta única para el archivo
    """
    base, ext = os.path.splitext(nombre_archivo)
    ruta = os.path.join(carpeta, nombre_archivo)
    
    # Si ya existe, es un duplicado
    if os.path.exists(ruta):
        if stats:
            stats["duplicados"] += 1
        
        if logger:
            logger(f"  ⚠️ DUPLICADO: {nombre_archivo} (se renombrará con sufijo)", "WARNING")
        
        contador = 1
        while os.path.exists(ruta):
            ruta = os.path.join(carpeta, f"{base}_{contador}{ext}")
            contador += 1
    
    return ruta
