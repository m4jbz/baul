# Este archivo/clase es el segundo despues de run.py, una vez ya seleccionada la USB, y verificada
# que no tiene la carpeta Baul/ se mostrara la opcion para crear uno nuevo.

import customtkinter as ctk
import os
from tkinter import filedialog, messagebox

import crypto_utils
import login_gui

class SetupWindow(ctk.CTk):
    def __init__(self, baul_path, key_file_path):
        super().__init__()

        # Rutas para el Baul/ y la llave
        self.baul_path = baul_path
        self.key_file_path = key_file_path
        self.credentials_path = os.path.dirname(key_file_path)

        self.title("Configuración del Baúl")
        self.geometry("400x250") # Se redujo la altura
        self.resizable(False, False)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        self.show_initial_options()

    # Muestra la opcion de crear baul
    def show_initial_options(self):
        self.clear_frame()

        label = ctk.CTkLabel(self.main_frame, text="No se ha encontrado un Baúl en esta USB.\nDebes crear uno nuevo para continuar.",
                             font=ctk.CTkFont(size=14))
        label.pack(pady=20, padx=10)

        #                                                                     - Funcion a ejecutar -
        btn_create = ctk.CTkButton(self.main_frame, text="Crear un nuevo Baúl", command=self.show_create_vault)
        btn_create.pack(pady=20, fill="x", padx=20)

    # Iniciar un Baul desde 0
    def show_create_vault(self):
        self.clear_frame()
        label = ctk.CTkLabel(self.main_frame, text="Crea tu Contraseña Maestra", font=ctk.CTkFont(size=16))
        label.pack(pady=15)

        # Se pide crear una contraseña
        self.pass_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Contraseña", show="*")
        self.pass_entry.pack(pady=5, fill="x", padx=20)
        
        self.confirm_pass_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Confirmar contraseña", show="*")
        self.confirm_pass_entry.pack(pady=5, fill="x", padx=20)

        #                                                                 - Funcion a ejecutar -
        btn_create = ctk.CTkButton(self.main_frame, text="Crear y Guardar", command=self.create_new_vault)
        btn_create.pack(pady=20, fill="x", padx=20)
        
        btn_back = ctk.CTkButton(self.main_frame, text="Volver", fg_color="transparent", border_width=1,
                                 command=self.show_initial_options)
        btn_back.pack(pady=5, fill="x", padx=20)

    def create_new_vault(self):
        password = self.pass_entry.get()
        confirm_password = self.confirm_pass_entry.get()

        # No se escribio la contraseña
        if not password or not confirm_password:
            messagebox.showerror("ERROR", "Ambos campos son obligatorios.")
            return

        # La contraseña inicial y la confirmación no coinciden
        if password != confirm_password:
            messagebox.showerror("ERROR", "Las contraseñas no coinciden.")
            return

        try:
            # Generar el contenido de la llave
            vault_key_content = crypto_utils.generate_vault_key(password)

            # Crear directorios
            os.makedirs(self.credentials_path, exist_ok=True)
            
            # Guardar el vault.key en la USB
            with open(self.key_file_path, "wb") as f:
                f.write(vault_key_content)
            
            self.launch_login()

        except Exception as e:
            messagebox.showerror("ERROR", f"No se pudo crear el Baúl: {e}")

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # Función para pasar al login en caso de exito de los casos anteriores
    def launch_login(self):
        self.destroy()
        login_app = login_gui.LoginWindow(baul_path=self.baul_path, key_file_path=self.key_file_path)
        login_app.mainloop()
