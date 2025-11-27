import logging
import tkinter as tk
from datetime import datetime

class GUILogHandler(logging.Handler):
    """Handler para redirigir logs a un widget de texto Tkinter"""
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        self.text_widget.tag_config("INFO", foreground="blue")
        self.text_widget.tag_config("WARNING", foreground="orange")
        self.text_widget.tag_config("ERROR", foreground="red")
        self.text_widget.tag_config("SUCCESS", foreground="green")

    def emit(self, record):
        msg = self.format(record)
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_msg = f"[{timestamp}] {msg}\n"
        
        def append():
            self.text_widget.insert(tk.END, full_msg, record.levelname)
            self.text_widget.see(tk.END)
        
        # Asegurar que se ejecute en el hilo principal
        self.text_widget.after(0, append)

def setup_logger(name, text_widget=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if text_widget:
        handler = GUILogHandler(text_widget)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger
