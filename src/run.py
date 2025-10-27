import customtkinter as ctk
import psutil
from pathlib import Path
from tkinter import messagebox

import setup_gui
import login_gui 

# Clase para poder seleccionar una USB si hay varias conectadas
class UsbSelector(ctk.CTkToplevel):
    def __init__(self, master, usbs):
        super().__init__(master)
        self.title("Seleccionar USB")
        self.geometry("350x200")
        self.transient(master)
        self.grab_set()

        self.selected_usb = None
        self.usb_var = ctk.StringVar(value=usbs[0].mountpoint)

        label = ctk.CTkLabel(self, text="Se detectaron varias USB.\nPor favor, selecciona una:")
        label.pack(pady=10, padx=10)

        for usb in usbs:
            rb = ctk.CTkRadioButton(self, text=f"{usb.mountpoint} ({usb.device})",
                                    variable=self.usb_var, value=usb.mountpoint)
            rb.pack(anchor="w", padx=20)

        button = ctk.CTkButton(self, text="Aceptar", command=self.on_select)
        button.pack(pady=20)

    def on_select(self):
        self.selected_usb = Path(self.usb_var.get())
        self.destroy()

    def get_selection(self):
        self.master.wait_window(self)
        return self.selected_usb

def find_usb():
    # Se busca la opción removable en las particiones del sistema
    # lo cual nos indica que es una USB
    partitions = psutil.disk_partitions()
    usbs = [p for p in partitions if 'removable' in p.opts or 'REMOVABLE' in p.opts]

    if len(usbs) == 0:
        return "NO_USB", None

    if len(usbs) > 1:
        return "MULTIPLE_USB", usbs

    return "ONE_USB", Path(usbs[0].mountpoint)

def handle_usb():
    # Verificar la USB primero, ANTES de crear cualquier ventana
    status, usb_info = find_usb()
    selected_path = None

    # Manejar los casos de la USB
    if status == "NO_USB":
        # Creamos una raíz temporal SOLO para el messagebox
        root_msg = ctk.CTk()
        root_msg.withdraw()
        messagebox.showerror("ERROR", "No se detectó ninguna unidad USB.\nPor favor, inserta una USB antes de iniciar el programa.")
        root_msg.destroy()
        return

    if status == "MULTIPLE_USB":
        # Creamos una raíz temporal SOLO para el selector
        root_selector = ctk.CTk()
        root_selector.withdraw()
        selector = UsbSelector(root_selector, usb_info)
        selected_path = selector.get_selection()
        root_selector.destroy()

        if not selected_path:
            return

    elif status == "ONE_USB":
        selected_path = usb_info

    # Definimos las rutas clave
    BAUL_PATH = selected_path / "Baul"
    CREDENTIALS_PATH = BAUL_PATH / ".credentials"
    KEY_FILE_PATH = CREDENTIALS_PATH / "vault.key"

    # Si no existe el directorio Baul, se usa setup_gui.py
    # para crearlo
    if not KEY_FILE_PATH.exists():
        setup_app = setup_gui.SetupWindow(baul_path=BAUL_PATH, key_file_path=KEY_FILE_PATH)
        setup_app.mainloop()
    # Si existe, se usa login_gui.py para iniciar sesión
    else:
        login_app = login_gui.LoginWindow(baul_path=BAUL_PATH, key_file_path=KEY_FILE_PATH)
        login_app.mainloop()

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    handle_usb()
