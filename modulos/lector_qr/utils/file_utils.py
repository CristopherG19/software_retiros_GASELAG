"""Utilidades para manejo de archivos y detección de duplicados."""

import os
import hashlib


def comparar_contenido_md5(archivo1, archivo2):
    """
    Compara dos archivos usando hash MD5.
    
    Args:
        archivo1: Ruta al primer archivo
        archivo2: Ruta al segundo archivo
        
    Returns:
        bool: True si son idénticos, False si diferentes o error
    """
    try:
        def calcular_hash(ruta):
            hash_md5 = hashlib.md5()
            with open(ruta, "rb") as f:
                # Leer en chunks de 4KB para eficiencia
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        
        hash1 = calcular_hash(archivo1)
        hash2 = calcular_hash(archivo2)
        
        return hash1 == hash2
        
    except (IOError, OSError) as e:
        print(f"Error comparando archivos: {e}")
        return False


def generar_ruta_unica(carpeta, nombre_archivo, archivo_origen=None, 
                       stats=None, logger=None, politica="renombrar", 
                       callback_pregunta=None):
    """
    Genera ruta única con políticas avanzadas de duplicados.
    
    Args:
        carpeta: Carpeta destino
        nombre_archivo: Nombre deseado
        archivo_origen: Ruta del archivo a copiar (para comparar contenido)
        stats: Diccionario de estadísticas
        logger: Función de logging
        politica: "renombrar", "preguntar", o "comparar"
        callback_pregunta: Función que retorna "sobrescribir"/"renombrar"/"saltar"
        
    Returns:
        tuple: (ruta_final, accion_tomada)
        - ruta_final: str o None (None = saltar archivo)
        - accion_tomada: "nuevo"/"sobrescrito"/"renombrado"/"saltado"
    """
    base, ext = os.path.splitext(nombre_archivo)
    ruta = os.path.join(carpeta, nombre_archivo)
    
    # Caso 1: Archivo no existe
    if not os.path.exists(ruta):
        return ruta, "nuevo"
    
    # Caso 2: Archivo existe - DUPLICADO
    if stats:
        stats["duplicados"] += 1
    
    # OPCIÓN C: Comparar contenido
    if politica == "comparar":
        if archivo_origen and comparar_contenido_md5(archivo_origen, ruta):
            if logger:
                logger(f"  [!] DUPLICADO IDENTICO: {nombre_archivo} (omitido)", "WARNING")
            return None, "saltado_identico"
        else:
            if logger:
                logger(f"  [!] DUPLICADO con diferente contenido: {nombre_archivo}", "WARNING")
            # Continuar a renombrar
    
    # OPCIÓN B: Preguntar al usuario
    if politica == "preguntar" and callback_pregunta:
        respuesta = callback_pregunta(nombre_archivo, ruta)
        
        if respuesta == "sobrescribir":
            if logger:
                logger(f"  [!] DUPLICADO: {nombre_archivo} (sobrescrito)", "WARNING")
            return ruta, "sobrescrito"
        
        elif respuesta == "saltar":
            if logger:
                logger(f"  [!] DUPLICADO: {nombre_archivo} (omitido por usuario)", "WARNING")
            return None, "saltado_usuario"
        
        # Si respuesta == "renombrar", continuar abajo
    
    # OPCIÓN A (default): Renombrar con sufijo
    if logger:
        logger(f"  [!] DUPLICADO: {nombre_archivo} (renombrado)", "WARNING")
    
    contador = 1
    while os.path.exists(ruta):
        ruta = os.path.join(carpeta, f"{base}_{contador}{ext}")
        contador += 1
    
    return ruta, "renombrado"
