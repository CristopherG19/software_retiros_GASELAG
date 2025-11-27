import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, scrolledtext, messagebox
from threading import Thread
import os
from modulos.procesador_excel.motor_excel import MotorExcel

class ProcesadorExcelTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        
        # Variables
        self.archivo_excel = tk.StringVar()
        self.hoja_plantilla = tk.StringVar()
        self.generar_pdf = tk.BooleanVar(value=True)
        self.carpeta_pdf = tk.StringVar(value=r"C:\retiro")
        self.imprimir = tk.BooleanVar(value=False)
        self.impresora_seleccionada = tk.StringVar()
        self.copias = tk.IntVar(value=1)
        
        self.motor = MotorExcel(self.log_callback)
        self.procesando = False
        self.hojas_disponibles = []
        
        self.setup_ui()
        
    def setup_ui(self):
        # --- Selección de Archivo ---
        file_frame = ttk.Labelframe(self, text="Archivo de Datos", padding=10)
        file_frame.pack(fill=X, pady=5)
        
        ttk.Entry(file_frame, textvariable=self.archivo_excel, state="readonly").pack(side=LEFT, fill=X, expand=YES, padx=5)
        ttk.Button(file_frame, text="Examinar Excel", command=self.seleccionar_excel).pack(side=LEFT, padx=5)
        
        # --- Configuración de Proceso ---
        config_frame = ttk.Labelframe(self, text="Configuración", padding=10)
        config_frame.pack(fill=X, pady=5)
        
        # Fila 1: Plantilla
        ttk.Label(config_frame, text="Plantilla:").grid(row=0, column=0, sticky=W, pady=5)
        self.combo_plantillas = ttk.Combobox(config_frame, textvariable=self.hoja_plantilla, state="readonly", width=30)
        self.combo_plantillas.grid(row=0, column=1, sticky=W, padx=5)
        
        # Fila 2: PDF
        ttk.Checkbutton(config_frame, text="Generar PDF", variable=self.generar_pdf, command=self.toggle_pdf).grid(row=1, column=0, sticky=W, pady=5)
        self.entry_pdf = ttk.Entry(config_frame, textvariable=self.carpeta_pdf, width=40)
        self.entry_pdf.grid(row=1, column=1, padx=5)
        self.btn_pdf = ttk.Button(config_frame, text="...", command=self.seleccionar_carpeta_pdf, width=3)
        self.btn_pdf.grid(row=1, column=2)
        
        # Fila 3: Impresión
        ttk.Checkbutton(config_frame, text="Imprimir Físico", variable=self.imprimir, command=self.toggle_print).grid(row=2, column=0, sticky=W, pady=5)
        
        # Frame para impresora y copias
        print_frame = ttk.Frame(config_frame)
        print_frame.grid(row=2, column=1, columnspan=2, sticky=W)
        
        self.combo_impresoras = ttk.Combobox(print_frame, textvariable=self.impresora_seleccionada, state="readonly", width=30)
        self.combo_impresoras.pack(side=LEFT, padx=5)
        
        self.spin_copias = ttk.Spinbox(print_frame, from_=1, to=10, textvariable=self.copias, width=5, state=DISABLED)
        self.spin_copias.pack(side=LEFT, padx=5)
        ttk.Label(print_frame, text="copias").pack(side=LEFT)
        
        # Cargar impresoras
        self.cargar_impresoras()
        
        # --- Botones ---
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=X, pady=10)
        
        self.btn_procesar = ttk.Button(
            btn_frame, 
            text="PROCESAR PLANTILLAS", 
            command=self.iniciar,
            bootstyle="success",
            width=25
        )
        self.btn_procesar.pack(side=LEFT, padx=5)
        
        self.btn_detener = ttk.Button(
            btn_frame, 
            text="Detener", 
            command=self.detener,
            bootstyle="danger",
            state=DISABLED
        )
        self.btn_detener.pack(side=LEFT, padx=5)
        
        # --- Progreso ---
        self.progress = ttk.Progressbar(self, mode='determinate', bootstyle="success-striped")
        self.progress.pack(fill=X, pady=5)
        
        self.lbl_progreso = ttk.Label(self, text="Esperando archivo...")
        self.lbl_progreso.pack(anchor=W)
        
        # --- Log ---
        log_frame = ttk.Labelframe(self, text="Log de Proceso", padding=5)
        log_frame.pack(fill=BOTH, expand=YES)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, state='normal', font=("Consolas", 9))
        self.log_text.pack(fill=BOTH, expand=YES)
        
        self.log_text.tag_config("INFO", foreground="#007bff")
        self.log_text.tag_config("SUCCESS", foreground="#28a745")
        self.log_text.tag_config("WARNING", foreground="#ffc107")
        self.log_text.tag_config("ERROR", foreground="#dc3545")

    def cargar_impresoras(self):
        try:
            import win32print
            printers = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
            self.combo_impresoras['values'] = printers
            
            # Seleccionar predeterminada
            default = win32print.GetDefaultPrinter()
            if default in printers:
                self.combo_impresoras.set(default)
            elif printers:
                self.combo_impresoras.current(0)
                
        except Exception as e:
            self.log_callback(f"Error cargando impresoras: {e}", "WARNING")
            self.combo_impresoras['values'] = ["Error cargando impresoras"]

    def toggle_pdf(self):
        state = NORMAL if self.generar_pdf.get() else DISABLED
        self.entry_pdf.config(state=state)
        self.btn_pdf.config(state=state)

    def toggle_print(self):
        state = NORMAL if self.imprimir.get() else DISABLED
        self.spin_copias.config(state=state)
        self.combo_impresoras.config(state="readonly" if state == NORMAL else DISABLED)

    def seleccionar_excel(self):
        archivo = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx;*.xlsm")])
        if archivo:
            self.archivo_excel.set(archivo)
            self.cargar_hojas(archivo)

    def seleccionar_carpeta_pdf(self):
        carpeta = filedialog.askdirectory()
        if carpeta:
            self.carpeta_pdf.set(carpeta)

    def cargar_hojas(self, archivo):
        self.log_callback("Leyendo estructura del archivo...", "INFO")
        try:
            hojas = self.motor.obtener_hojas(archivo)
            # Filtrar hojas que parecen plantillas (empiezan con FORM o similar, o mostrar todas)
            self.hojas_disponibles = hojas
            self.combo_plantillas['values'] = hojas
            
            # Intentar seleccionar la primera que parezca plantilla
            for hoja in hojas:
                if "FORM" in hoja.upper():
                    self.combo_plantillas.set(hoja)
                    break
            if not self.combo_plantillas.get() and hojas:
                self.combo_plantillas.current(0)
                
            self.log_callback(f"Archivo cargado. {len(hojas)} hojas encontradas.", "SUCCESS")
        except Exception as e:
            self.log_callback(f"Error leyendo archivo: {e}", "ERROR")

    def log_callback(self, msg, level="INFO"):
        self.log_text.insert(tk.END, f"[{level}] {msg}\n", level)
        self.log_text.see(tk.END)

    def iniciar(self):
        if self.procesando: return
        
        if not self.archivo_excel.get():
            messagebox.showwarning("Falta archivo", "Seleccione un archivo Excel primero.")
            return
            
        if not self.hoja_plantilla.get():
            messagebox.showwarning("Falta plantilla", "Seleccione la hoja de plantilla.")
            return

        self.procesando = True
        self.btn_procesar.config(state=DISABLED)
        self.btn_detener.config(state=NORMAL)
        self.log_text.delete(1.0, tk.END)
        
        config = {
            'archivo_excel': self.archivo_excel.get(),
            'hoja_plantilla': self.hoja_plantilla.get(),
            'generar_pdf': self.generar_pdf.get(),
            'carpeta_pdf': self.carpeta_pdf.get(),
            'imprimir': self.imprimir.get(),
            'impresora': self.impresora_seleccionada.get(),
            'copias': self.copias.get()
        }
        
        Thread(target=self.proceso_thread, args=(config,), daemon=True).start()

    def detener(self):
        self.motor.detener()
        self.log_callback("Solicitando detención...", "WARNING")

    def proceso_thread(self, config):
        def progress_cb(idx, total, actual):
            porcentaje = (idx / total) * 100
            self.progress['value'] = porcentaje
            self.lbl_progreso.config(text=f"Procesando {idx}/{total}: {actual}")
        
        stats = self.motor.procesar(config, progress_cb)
        
        self.after(0, lambda: self.finalizar(stats))

    def finalizar(self, stats):
        self.procesando = False
        self.btn_procesar.config(state=NORMAL)
        self.btn_detener.config(state=DISABLED)
        self.progress['value'] = 0
        self.lbl_progreso.config(text="Proceso finalizado")
        
        msg = f"Proceso completado.\nExitosos: {stats['exitosos']}\nFallidos: {stats['fallidos']}"
        if stats['fallidos'] > 0:
            messagebox.showwarning("Completado con errores", msg)
        else:
            messagebox.showinfo("Éxito", msg)
