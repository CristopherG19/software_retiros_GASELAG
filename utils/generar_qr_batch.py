"""
Script para generar múltiples códigos QR en batch (lote) de forma paralela.
Optimizado para máximo rendimiento.

Uso:
    python generar_qr_batch.py "TEXTO1|TEXTO2|TEXTO3" "CARPETA_SALIDA"

Ejemplo:
    python generar_qr_batch.py "123|456|789" "C:\temp\qr"
    
    Generará:
        C:\temp\qr\qr_0.png (con código 123)
        C:\temp\qr\qr_1.png (con código 456)
        C:\temp\qr\qr_2.png (con código 789)
"""

import sys
import qrcode
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import time


def generar_qr_individual(args):
    """
    Genera un código QR individual.
    
    Args:
        args (tuple): (índice, texto, carpeta_salida, tamaño)
    
    Returns:
        tuple: (índice, ruta_archivo, éxito)
    """
    indice, texto, carpeta_salida, tamano = args
    
    try:
        # Configurar QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=3,
            border=1,
        )
        
        qr.add_data(texto)
        qr.make(fit=True)
        
        # Crear imagen
        img = qr.make_image(fill_color="black", back_color="white")
        img = img.resize((tamano, tamano))
        
        # Guardar con índice en el nombre
        ruta_archivo = Path(carpeta_salida) / f"qr_{indice}.png"
        img.save(ruta_archivo)
        
        return (indice, str(ruta_archivo), True)
        
    except Exception as e:
        print(f"Error en QR {indice}: {e}", file=sys.stderr)
        return (indice, None, False)


def generar_qr_batch(textos, carpeta_salida, tamano=60, max_workers=4):
    """
    Genera múltiples códigos QR en paralelo.
    
    Args:
        textos (list): Lista de textos para generar QRs
        carpeta_salida (str): Carpeta donde guardar los QRs
        tamano (int): Tamaño de cada QR en píxeles
        max_workers (int): Número de hilos paralelos
    
    Returns:
        dict: Diccionario {índice: ruta_archivo}
    """
    # Crear carpeta si no existe
    Path(carpeta_salida).mkdir(parents=True, exist_ok=True)
    
    # Preparar argumentos para cada QR
    args_list = [
        (i, texto, carpeta_salida, tamano)
        for i, texto in enumerate(textos)
        if texto.strip()  # Ignorar textos vacíos
    ]
    
    # Generar en paralelo
    resultados = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for indice, ruta, exito in executor.map(generar_qr_individual, args_list):
            if exito:
                resultados[indice] = ruta
    
    return resultados


def main():
    """Función principal para uso desde línea de comandos."""
    if len(sys.argv) < 2:
        print("Uso: python generar_qr_batch.py 'TEXTO1|TEXTO2|TEXTO3' 'CARPETA_SALIDA'")
        print("  O: python generar_qr_batch.py --file 'ARCHIVO.txt' 'CARPETA_SALIDA'")
        print("Ejemplo: python generar_qr_batch.py '123|456|789' 'C:\\temp\\qr'")
        sys.exit(1)
    
    # Verificar si se usa modo archivo
    usar_archivo = False
    if sys.argv[1] == '--file':
        usar_archivo = True
        if len(sys.argv) < 4:
            print("ERROR: Faltan argumentos para modo --file")
            sys.exit(1)
        archivo_textos = sys.argv[2]
        carpeta_salida = sys.argv[3]
    else:
        if len(sys.argv) < 3:
            print("ERROR: Faltan argumentos")
            sys.exit(1)
        textos_str = sys.argv[1]
        carpeta_salida = sys.argv[2]
    
    # Leer textos según el modo
    if usar_archivo:
        try:
            with open(archivo_textos, 'r', encoding='utf-8') as f:
                textos_str = f.read().strip()
            print(f"Textos leídos desde archivo: {len(textos_str)} caracteres", file=sys.stderr)
        except Exception as e:
            print(f"ERROR al leer archivo {archivo_textos}: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Tamaño opcional
    tamano = 60
    if (usar_archivo and len(sys.argv) >= 5) or (not usar_archivo and len(sys.argv) >= 4):
        try:
            tamano = int(sys.argv[-1])
        except ValueError:
            print("ADVERTENCIA: Tamaño inválido, usando 60 por defecto", file=sys.stderr)
    
    # Separar textos por pipe |
    textos = textos_str.split("|")
    
    print(f"Generando {len(textos)} códigos QR...", file=sys.stderr)
    inicio = time.time()
    
    # Generar en batch
    resultados = generar_qr_batch(textos, carpeta_salida, tamano)
    
    tiempo = time.time() - inicio
    
    # Reportar resultados
    print(f"Generados {len(resultados)} de {len(textos)} QRs en {tiempo:.2f} segundos", file=sys.stderr)
    
    # Imprimir rutas para que VBA las pueda leer
    for i in range(len(textos)):
        if i in resultados:
            print(resultados[i])
        else:
            print("")  # Línea vacía si falló
    
    sys.exit(0 if len(resultados) == len(textos) else 1)


if __name__ == "__main__":
    main()
