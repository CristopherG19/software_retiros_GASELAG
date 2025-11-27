import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
import os
from utils.generar_qr_batch import generar_qr_batch

class GeneradorQRTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        
        self.texto_qr = tk.StringVar()
        self.carpeta_salida = tk.StringVar(value=r"C:\temp\qr_output")
        self.tamano = tk.IntVar(value=200)
        
        self.setup_ui()
        
    def setup_ui(self):
        # --- Entrada de Texto ---
        input_frame = ttk.Labelframe(self, text="Datos del QR", padding=10)
        input_frame.pack(fill=X, pady=5)
        
        ttk.Label(input_frame, text="Texto/URL:").pack(anchor=W)
        ttk.Entry(input_frame, textvariable=self.texto_qr).pack(fill=X, pady=5)
        
        ttk.Label(input_frame, text="Para múltiples QRs, separe con '|' (ej: 123|456|789)").pack(anchor=W, pady=(5,0))
        
        # --- Configuración ---
        config_frame = ttk.Labelframe(self, text="Configuración", padding=10)
        config_frame.pack(fill=X, pady=5)
        
        # Carpeta
        ttk.Label(config_frame, text="Carpeta Salida:").grid(row=0, column=0, sticky=W)
        ttk.Entry(config_frame, textvariable=self.carpeta_salida).grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(config_frame, text="...", command=self.seleccionar_carpeta).grid(row=0, column=2)
        config_frame.columnconfigure(1, weight=1)
        
        # Tamaño
        ttk.Label(config_frame, text="Tamaño (px):").grid(row=1, column=0, sticky=W, pady=5)
        ttk.Spinbox(config_frame, from_=50, to=1000, textvariable=self.tamano).grid(row=1, column=1, sticky=W, padx=5, pady=5)
        
        # --- Botón ---
        self.btn_generar = ttk.Button(
            self, 
            text="Generar QR", 
            command=self.generar,
            bootstyle="primary",
            width=20
        )
        self.btn_generar.pack(pady=20)
        
        # --- Vista Previa (Placeholder) ---
        self.preview_frame = ttk.Labelframe(self, text="Vista Previa (Último generado)", padding=10)
        self.preview_frame.pack(fill=BOTH, expand=YES)
        
        self.lbl_preview = ttk.Label(self.preview_frame, text="Genera un QR para ver la vista previa")
        self.lbl_preview.pack(expand=YES)

    def seleccionar_carpeta(self):
        path = filedialog.askdirectory()
        if path: self.carpeta_salida.set(path)

    def generar(self):
        texto = self.texto_qr.get().strip()
        if not texto:
            messagebox.showwarning("Error", "Ingrese texto para el QR")
            return
            
        carpeta = self.carpeta_salida.get()
        if not os.path.exists(carpeta):
            try:
                os.makedirs(carpeta)
            except:
                messagebox.showerror("Error", "No se pudo crear la carpeta de salida")
                return
                
        # Separar por pipes
        textos = texto.split('|')
        
        try:
            resultados = generar_qr_batch(textos, carpeta, self.tamano.get())
            
            if resultados:
                msg = f"Se generaron {len(resultados)} códigos QR en:\n{carpeta}"
                messagebox.showinfo("Éxito", msg)
                
                # Mostrar el primero como preview
                first_path = list(resultados.values())[0]
                self.mostrar_preview(first_path)
            else:
                messagebox.showerror("Error", "No se generaron QRs")
                
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {e}")

    def mostrar_preview(self, path):
        try:
            from PIL import Image, ImageTk
            img = Image.open(path)
            # Redimensionar para preview si es muy grande
            img.thumbnail((300, 300))
            photo = ImageTk.PhotoImage(img)
            
            self.lbl_preview.config(image=photo, text="")
            self.lbl_preview.image = photo # Keep reference
        except Exception as e:
            self.lbl_preview.config(text=f"No se pudo cargar vista previa: {e}")
