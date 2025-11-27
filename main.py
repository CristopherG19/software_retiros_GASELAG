import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import sys
import os

# Importar módulos (se crearán próximamente)
from modulos.lector_qr.gui_lector import LectorQRTab
from modulos.procesador_excel.gui_procesador import ProcesadorExcelTab
from modulos.generador_qr.gui_generador import GeneradorQRTab

class QRMasterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Master v2.0")
        self.root.geometry("1100x800")
        
        # Configurar tema
        self.style = ttk.Style(theme="darkly")
        
        # Contenedor principal
        self.main_container = ttk.Frame(self.root, padding=10)
        self.main_container.pack(fill=BOTH, expand=YES)
        
        # Título
        title_frame = ttk.Frame(self.main_container)
        title_frame.pack(fill=X, pady=(0, 10))
        
        ttk.Label(
            title_frame, 
            text="QR Master Suite", 
            font=("Segoe UI", 24, "bold"),
            bootstyle="inverse-primary"
        ).pack(side=LEFT, padx=5)
        
        ttk.Label(
            title_frame,
            text="v2.0",
            font=("Segoe UI", 12),
            bootstyle="secondary"
        ).pack(side=LEFT, padx=5, pady=(10, 0))

        # Notebook (Pestañas)
        self.notebook = ttk.Notebook(self.main_container, bootstyle="primary")
        self.notebook.pack(fill=BOTH, expand=YES)
        
        # --- Pestaña 1: Procesar Excel (Prioridad) ---
        self.tab_excel = ProcesadorExcelTab(self.notebook)
        self.notebook.add(self.tab_excel, text="Procesar Plantillas")
        
        # --- Pestaña 2: Leer QR ---
        self.tab_lector = LectorQRTab(self.notebook)
        self.notebook.add(self.tab_lector, text="Leer y Renombrar")
        
        # --- Pestaña 3: Generar QR ---
        self.tab_generador = GeneradorQRTab(self.notebook)
        self.notebook.add(self.tab_generador, text="Generador Simple")
        
        # Barra de estado
        self.status_var = tk.StringVar(value="Listo")
        self.status_bar = ttk.Label(
            self.root, 
            textvariable=self.status_var,
            relief=SUNKEN,
            anchor=W,
            padding=(5, 2)
        )
        self.status_bar.pack(fill=X, side=BOTTOM)

    def init_placeholder_tab(self, parent, text):
        """Helper para mostrar contenido temporal"""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill=BOTH, expand=YES)
        
        ttk.Label(
            frame, 
            text="En Construcción", 
            font=("Segoe UI", 48)
        ).pack(pady=20)
        
        ttk.Label(
            frame, 
            text=text, 
            font=("Segoe UI", 16)
        ).pack(pady=10)

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = QRMasterApp(root)
    root.mainloop()
