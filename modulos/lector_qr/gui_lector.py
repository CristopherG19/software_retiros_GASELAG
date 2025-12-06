import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, scrolledtext
from threading import Thread
import os
import sys
from modulos.lector_qr.motor_qr import MotorQR

class LectorQRTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        
        # Variables
        # Detectar Poppler (Bundled vs Local)
        bundled_poppler = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "poppler", "Library", "bin")
        
        # Mejor estrategia: buscar en la raíz del ejecutable/script
        base_path = os.getcwd()
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
            
        possible_paths = [
            os.path.join(base_path, "poppler", "Library", "bin"),
            r"C:\poppler\Library\bin"
        ]
        
        default_poppler = r"C:\poppler\Library\bin"
        for p in possible_paths:
            if os.path.exists(p):
                default_poppler = p
                break

        self.carpeta_entrada = tk.StringVar(value=r"C:\Escaneos\Entrada")
        self.carpeta_salida = tk.StringVar(value=r"C:\Escaneos\Renombrados")
        self.carpeta_error = tk.StringVar(value=r"C:\Escaneos\SinQR")
        self.poppler_path = tk.StringVar(value=default_poppler)
        
        self.motor = MotorQR(self.log_callback)
        self.procesando = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # --- Configuración ---
        config_frame = ttk.Labelframe(self, text="Configuración", padding=10)
        config_frame.pack(fill=X, pady=5)
        
        self.crear_selector(config_frame, "Entrada:", self.carpeta_entrada, 0)
        self.crear_selector(config_frame, "Salida:", self.carpeta_salida, 1)
        self.crear_selector(config_frame, "Sin QR:", self.carpeta_error, 2)
        self.crear_selector(config_frame, "Poppler:", self.poppler_path, 3)
        
        # --- Botones ---
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=X, pady=10)
        
        self.btn_iniciar = ttk.Button(
            btn_frame, 
            text="Iniciar", 
            command=self.iniciar,
            bootstyle="success"
        )
        self.btn_iniciar.pack(side=LEFT, padx=5)
        
        self.btn_detener = ttk.Button(
            btn_frame, 
            text="Detener", 
            command=self.detener,
            bootstyle="danger",
            state=DISABLED
        )
        self.btn_detener.pack(side=LEFT, padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Limpiar Log", 
            command=self.limpiar_log,
            bootstyle="secondary-outline"
        ).pack(side=LEFT, padx=5)
        
        # --- Estadísticas ---
        stats_frame = ttk.Labelframe(self, text="Estadísticas", padding=10)
        stats_frame.pack(fill=X, pady=5)
        
        self.lbl_stats = ttk.Label(
            stats_frame, 
            text="Procesados: 0 | Exitosos: 0 | Fallidos: 0 | Duplicados: 0",
            font=("Segoe UI", 10, "bold")
        )
        self.lbl_stats.pack()
        
        # --- Progreso ---
        self.progress = ttk.Progressbar(self, mode='determinate', bootstyle="success-striped")
        self.progress.pack(fill=X, pady=5)
        
        self.lbl_progreso = ttk.Label(self, text="Listo")
        self.lbl_progreso.pack(anchor=W)
        
        # --- Log ---
        log_frame = ttk.Labelframe(self, text="Log", padding=5)
        log_frame.pack(fill=BOTH, expand=YES)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, state='normal', font=("Consolas", 9))
        self.log_text.pack(fill=BOTH, expand=YES)
        
        # Tags de colores
        self.log_text.tag_config("INFO", foreground="#007bff")
        self.log_text.tag_config("SUCCESS", foreground="#28a745")
        self.log_text.tag_config("WARNING", foreground="#ffc107")
        self.log_text.tag_config("ERROR", foreground="#dc3545")

    def crear_selector(self, parent, label, variable, row):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky=W, pady=2)
        ttk.Entry(parent, textvariable=variable).grid(row=row, column=1, sticky="ew", padx=5, pady=2)
        ttk.Button(parent, text="...", command=lambda: self.seleccionar(variable), width=3).grid(row=row, column=2, pady=2)
        parent.columnconfigure(1, weight=1)

    def seleccionar(self, variable):
        path = filedialog.askdirectory()
        if path: variable.set(path)

    def log_callback(self, msg, level="INFO"):
        self.log_text.insert(tk.END, f"[{level}] {msg}\n", level)
        self.log_text.see(tk.END)

    def limpiar_log(self):
        self.log_text.delete(1.0, tk.END)
        self.lbl_stats.config(text="Procesados: 0 | Exitosos: 0 | Fallidos: 0 | Duplicados: 0")

    def iniciar(self):
        if self.procesando: return
        
        if not os.path.exists(self.carpeta_entrada.get()):
            self.log_callback("Carpeta de entrada no existe", "ERROR")
            return

        self.procesando = True
        self.btn_iniciar.config(state=DISABLED)
        self.btn_detener.config(state=NORMAL)
        self.limpiar_log()
        
        Thread(target=self.proceso_thread, daemon=True).start()

    def detener(self):
        self.btn_detener.config(state=DISABLED)
        self.motor.detener()
        self.log_callback("Deteniendo proceso... (esto puede tardar unos segundos al finalizar el archivo actual)", "WARNING")

    def proceso_thread(self):
        def progress_cb(idx, total, archivo):
            porcentaje = (idx / total) * 100
            self.progress['value'] = porcentaje
            self.lbl_progreso.config(text=f"Procesando {idx}/{total}: {archivo}")
        
        stats = self.motor.procesar_directorio(
            self.carpeta_entrada.get(),
            self.carpeta_salida.get(),
            self.carpeta_error.get(),
            self.poppler_path.get(),
            progress_cb
        )
        
        # Actualizar UI final
        self.after(0, lambda: self.finalizar(stats))

    def finalizar(self, stats):
        self.procesando = False
        self.btn_iniciar.config(state=NORMAL)
        self.btn_detener.config(state=DISABLED)
        self.progress['value'] = 0
        self.lbl_progreso.config(text="Listo")
        
        self.lbl_stats.config(
            text=f"Procesados: {stats['procesados']} | Exitosos: {stats['exitosos']} | Fallidos: {stats['fallidos']} | Duplicados: {stats.get('duplicados', 0)}"
        )
        
        if stats['fallidos'] == 0 and stats['procesados'] > 0:
            self.log_callback("¡Proceso completado con éxito!", "SUCCESS")
        else:
            self.log_callback("Proceso finalizado con observaciones", "INFO")
