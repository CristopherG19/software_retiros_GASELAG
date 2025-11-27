# QR Master Suite v2.0

Aplicación de escritorio unificada para la gestión de documentos y códigos QR. Reemplaza las antiguas macros de Excel con una solución 100% Python, moderna y robusta.

## 🚀 Características

### 1. 📊 Procesador de Plantillas (Excel)
- **Automatización Completa**: Lee datos de Excel, genera códigos QR en lote y rellena plantillas.
- **Exportación PDF**: Genera archivos PDF manteniendo el diseño exacto de tus plantillas originales.
- **Impresión Directa**: Envía los documentos a la impresora seleccionada automáticamente.
- **Soporte de Impresoras**: Selecciona fácilmente qué impresora utilizar.

### 2. 📖 Lector y Renombrado
- **Organización Automática**: Escanea carpetas de PDFs o imágenes.
- **Detección QR**: Lee el código QR y renombra el archivo basado en su contenido.
- **Clasificación**: Separa automáticamente los archivos procesados de los que no tienen QR.

### 3. 📝 Generador Simple
- **Herramienta Rápida**: Crea códigos QR individuales o en lista sin necesidad de Excel.
- **Vista Previa**: Visualiza el QR generado al instante.

## 🛠️ Instalación y Uso

### Opción A: Ejecutable (Recomendado)
Simplemente ejecuta `QR Master.exe` ubicado en la carpeta `dist/QR Master`. No requiere instalación de Python.

### Opción B: Código Fuente
1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Ejecutar la aplicación:
   ```bash
   python main.py
   ```

## 📂 Estructura del Proyecto

- `main.py`: Punto de entrada de la aplicación.
- `modulos/`: Contiene la lógica de cada pestaña (Excel, Lector, Generador).
- `utils/`: Utilidades compartidas (Logger, Generador Batch).
- `dist/`: Contiene el ejecutable compilado.
- `archive/`: Versiones antiguas y backups.

## 📄 Documentación
Ver [MANUAL_USUARIO.md](MANUAL_USUARIO.md) para instrucciones detalladas de uso.
