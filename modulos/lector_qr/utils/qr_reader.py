"""Utilidad para lectura de códigos QR de imágenes."""

from pyzbar.pyzbar import decode


def leer_qr(imagen):
    """
    Lee un código QR de una imagen.
    
    Args:
        imagen: Objeto PIL Image
        
    Returns:
        str: Texto del código QR o None si no se encontró
    """
    try:
        codigos = decode(imagen)
        if codigos:
            return codigos[0].data.decode("utf-8")
    except Exception:
        pass
    return None
