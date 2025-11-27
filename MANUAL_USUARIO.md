# 📘 Manual de Usuario - QR Master v2.0

Bienvenido a **QR Master**, la suite completa para gestión de documentos con códigos QR. Esta aplicación reemplaza las antiguas macros de Excel y scripts sueltos con una interfaz moderna y unificada.

---

## 🚀 Inicio Rápido

1. Ejecute `main.py` (o el ejecutable `QR Master.exe` si lo construyó).
2. Verá 3 pestañas principales:

### 📊 1. Procesar Plantillas (Reemplazo de Macro)
Uso para generar actas masivas desde Excel.

1. **Archivo de Datos**: Seleccione su Excel (`.xlsm` o `.xlsx`) que contiene la hoja `DATA`.
2. **Plantilla**: Seleccione la hoja que usará como formato (ej: `FORM1A`).
3. **Configuración**:
   - **Generar PDF**: Marque para crear archivos PDF automáticamente.
   - **Carpeta PDF**: Elija dónde se guardarán.
   - **Imprimir**: Marque si desea enviar directamente a la impresora.
4. Presione **▶️ PROCESAR PLANTILLAS**.

> **Nota**: Excel se abrirá en segundo plano. No lo cierre manualmente mientras procesa.

### 📖 2. Leer y Renombrar
Uso para procesar documentos escaneados.

1. **Entrada**: Carpeta con los PDFs/Imágenes escaneados.
2. **Salida**: Carpeta donde se moverán los archivos renombrados.
3. **Sin QR**: Carpeta para archivos donde no se detectó código.
4. Presione **▶️ Iniciar**.

### 📝 3. Generador Simple
Uso para crear QRs rápidos sin Excel.

1. Escriba el texto o URL.
2. Para múltiples QRs, sepárelos con `|` (ej: `Codigo1|Codigo2`).
3. Presione **✨ Generar QR**.

---

## 🔧 Solución de Problemas

**Error: "No se encuentra Poppler"**
- Asegúrese de tener Poppler instalado y la ruta configurada en la pestaña "Leer y Renombrar".

**Error: Excel no responde**
- Si detiene el proceso forzosamente, Excel puede quedar abierto en segundo plano.
- Abra el Administrador de Tareas y cierre los procesos `Excel.exe`.

**Error: Dependencias faltantes**
- Ejecute `pip install -r requirements.txt`.

---

## 📞 Soporte
Desarrollado con Python 3.13 y ttkbootstrap.
