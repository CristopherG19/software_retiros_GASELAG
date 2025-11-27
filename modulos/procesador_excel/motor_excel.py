import os
import time
import win32com.client
import pythoncom
import openpyxl
from pathlib import Path
from utils.generar_qr_batch import generar_qr_batch

class MotorExcel:
    def __init__(self, logger_callback=None):
        self.stop_requested = False
        self.callback = logger_callback

    def log(self, msg, level="INFO"):
        if self.callback:
            self.callback(msg, level)
        else:
            print(f"[{level}] {msg}")

    def detener(self):
        self.stop_requested = True

    def obtener_hojas(self, ruta_excel):
        """Obtiene la lista de hojas del archivo Excel sin abrir la app completa"""
        try:
            wb = openpyxl.load_workbook(ruta_excel, read_only=True, keep_vba=True)
            hojas = wb.sheetnames
            wb.close()
            return hojas
        except Exception as e:
            self.log(f"Error leyendo hojas: {e}", "ERROR")
            return []

    def procesar(self, config, progress_callback=None):
        """
        Procesa el archivo Excel.
        config = {
            'archivo_excel': str,
            'hoja_plantilla': str,
            'generar_pdf': bool,
            'carpeta_pdf': str,
            'imprimir': bool,
            'copias': int,
            'columna_suministro': int (0-based, default 17 para R)
        }
        """
        self.stop_requested = False
        stats = {"procesados": 0, "exitosos": 0, "fallidos": 0}
        
        excel_app = None
        wb = None
        
        try:
            # 1. Leer datos con openpyxl (más rápido y seguro para lectura)
            self.log("Leyendo datos del Excel...", "INFO")
            wb_data = openpyxl.load_workbook(config['archivo_excel'], data_only=True)
            ws_data = wb_data['DATA']
            
            # Obtener datos y suministros
            filas = []
            suministros = []
            
            # Asumimos que la fila 1 son encabezados
            for row in ws_data.iter_rows(min_row=2, values_only=True):
                if row[0] is None: continue # Saltar filas vacías
                filas.append(row)
                # Columna R es índice 17
                suministro = str(row[17]) if len(row) > 17 and row[17] else "SIN_SUMINISTRO"
                suministros.append(suministro)
            
            wb_data.close()
            
            total = len(filas)
            if total == 0:
                self.log("No se encontraron datos en la hoja DATA", "WARNING")
                return stats
                
            self.log(f"Se encontraron {total} registros", "INFO")

            # 2. Generar QRs en Batch
            self.log("Generando códigos QR...", "INFO")
            carpeta_temp = os.path.join(os.environ['TEMP'], f"qr_batch_{int(time.time())}")
            os.makedirs(carpeta_temp, exist_ok=True)
            
            # Usar la utilidad existente
            rutas_qr = generar_qr_batch(suministros, carpeta_temp)
            
            # 3. Iniciar Excel para exportación (COM)
            # 3. Iniciar Excel para exportación (COM)
            self.log("Iniciando Excel...", "INFO")
            pythoncom.CoInitialize()
            
            # Usar DispatchEx para forzar nueva instancia y evitar conflictos
            excel_app = win32com.client.DispatchEx("Excel.Application")
            excel_app.Visible = False
            excel_app.DisplayAlerts = False
            
            # Asegurar ruta absoluta y normalizada
            ruta_abs = os.path.abspath(config['archivo_excel'])
            if not os.path.exists(ruta_abs):
                raise FileNotFoundError(f"No se encuentra el archivo: {ruta_abs}")
                
            self.log(f"Abriendo: {ruta_abs}", "INFO")
            wb = excel_app.Workbooks.Open(ruta_abs)
            
            if wb is None:
                raise Exception("Excel no pudo abrir el archivo (Workbooks.Open retornó None)")
                
            ws_plantilla = wb.Sheets(config['hoja_plantilla'])
            
            # 4. Procesar cada registro
            for idx, fila in enumerate(filas):
                if self.stop_requested:
                    self.log("Detenido por usuario", "WARNING")
                    break
                
                suministro = suministros[idx]
                
                # Callback progreso
                if progress_callback:
                    progress_callback(idx + 1, total, suministro)
                
                try:
                    # Copiar datos a la plantilla (Fila 4 como en la macro original)
                    # La macro original pegaba en R4. Asumimos que la plantilla espera los datos ahí
                    # O mejor, replicamos la lógica de "pegar valores"
                    # En la macro: DataSheet.Cells(i, 1).Resize(...).Copy -> TemplateSheet.Range("R4").PasteSpecial
                    
                    # En COM, es más lento celda por celda. Mejor escribir el array.
                    # Convertir tupla a lista para COM
                    fila_list = list(fila)
                    # Rango R4 es columna 18, fila 4
                    # ws_plantilla.Range("R4").Resize(1, len(fila_list)).Value = fila_list
                    # NOTA: La macro original pegaba en R4. Vamos a respetar eso.
                    
                    # Limpiar contenido previo
                    # ws_plantilla.Range("R4").EntireRow.ClearContents # No, solo el rango
                    
                    # Escribir datos
                    start_col = 18 # Columna R
                    for c_idx, valor in enumerate(fila_list):
                        ws_plantilla.Cells(4, start_col + c_idx).Value = valor
                        
                    # Insertar QR
                    # Borrar QR anterior si existe
                    try:
                        ws_plantilla.Shapes("CODIGO_QR_ACTUAL").Delete()
                    except:
                        pass
                        
                    ruta_qr = rutas_qr.get(idx)
                    if ruta_qr and os.path.exists(ruta_qr):
                        # Insertar en M8 (según macro original)
                        celda_qr = ws_plantilla.Range("M8")
                        pic = ws_plantilla.Shapes.AddPicture(
                            str(ruta_qr), 
                            False, # LinkToFile
                            True,  # SaveWithDocument
                            celda_qr.Left, 
                            celda_qr.Top, 
                            60, 60
                        )
                        pic.Name = "CODIGO_QR_ACTUAL"
                    else:
                        self.log(f"No se generó QR para {suministro}", "WARNING")

                    # Exportar PDF
                    if config['generar_pdf']:
                        nombre_pdf = f"{suministro}.pdf"
                        # Limpiar caracteres inválidos
                        nombre_pdf = "".join([c for c in nombre_pdf if c.isalnum() or c in " .-_"])
                        ruta_pdf = os.path.join(config['carpeta_pdf'], nombre_pdf)
                        
                        ws_plantilla.ExportAsFixedFormat(0, ruta_pdf) # 0 = xlTypePDF
                        self.log(f"  PDF: {nombre_pdf}", "SUCCESS")
                    
                    # Imprimir
                    if config['imprimir']:
                        try:
                            # Intentar cambiar la impresora activa si se especificó
                            impresora = config.get('impresora')
                            if impresora:
                                # Excel requiere "Nombre en Puerto" (ej: "HP Deskjet en Ne01:")
                                # Sin embargo, a veces funciona solo con el nombre o cambiando la default del sistema (no recomendado)
                                # Intentaremos pasar el nombre a PrintOut (ActivePrinter argument)
                                # Nota: PrintOut(From, To, Copies, Preview, ActivePrinter, PrintToFile, Collate, PrToFileName)
                                ws_plantilla.PrintOut(Copies=config['copias'], ActivePrinter=impresora)
                                self.log(f"  Enviado a: {impresora}", "INFO")
                            else:
                                ws_plantilla.PrintOut(Copies=config['copias'])
                                self.log(f"  Enviado a impresora predeterminada", "INFO")
                        except Exception as e:
                            self.log(f"Error al imprimir: {e}", "WARNING")
                            # Intentar fallback sin especificar impresora
                            try:
                                ws_plantilla.PrintOut(Copies=config['copias'])
                                self.log(f"  Enviado a impresora predeterminada (Fallback)", "INFO")
                            except:
                                pass
                        
                    stats["procesados"] += 1
                    stats["exitosos"] += 1
                    
                except Exception as e:
                    self.log(f"Error en registro {idx+1}: {e}", "ERROR")
                    stats["fallidos"] += 1

        except Exception as e:
            self.log(f"Error crítico: {e}", "ERROR")
        finally:
            # Cerrar Excel
            if wb:
                wb.Close(SaveChanges=False)
            if excel_app:
                excel_app.Quit()
            pythoncom.CoUninitialize()
            
            self.log("Proceso finalizado", "INFO")
            return stats
