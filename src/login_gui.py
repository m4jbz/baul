import customtkinter as ctk

import crypto_utils
import main_app

class LoginWindow(ctk.CTk):
    def __init__(self, baul_path, key_file_path):
        super().__init__()

        self.baul_path = baul_path
        self.key_file_path = key_file_path

        self.title("Desbloquear Baúl")
        self.geometry("350x200")
        self.resizable(False, False)

        self.grid_columnconfigure(0, weight=1)

        label = ctk.CTkLabel(self, text="Ingresa tu Contraseña", font=ctk.CTkFont(size=16))
        label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.pass_entry = ctk.CTkEntry(self, placeholder_text="Contraseña", show="*", width=300)
        self.pass_entry.grid(row=1, column=0, padx=20, pady=5)
        # Bindeamos Enter a la función de login
        self.pass_entry.bind("<Return>", self.attempt_login)

        self.login_button = ctk.CTkButton(self, text="Desbloquear", command=self.attempt_login, width=300)
        self.login_button.grid(row=2, column=0, padx=20, pady=10)

        self.status_label = ctk.CTkLabel(self, text="", text_color="red")
        self.status_label.grid(row=3, column=0, padx=20, pady=(0, 10))

        # Enfocar el campo de contraseña al iniciar
        self.pass_entry.focus()

    def attempt_login(self, event=None):
        password = self.pass_entry.get()
        if not password:
            self.status_label.configure(text="Ingresa una contraseña.")
            return

        self.status_label.configure(text="Descifrando...", text_color="gray")
        self.login_button.configure(state="disabled")
        self.pass_entry.configure(state="disabled")
        self.update_idletasks() # Forzar actualización de UI

        try:
            # Leer el contenido del 'vault.key'
            with open(self.key_file_path, "rb") as f:
                vault_key_content = f.read()

            # Intentar desbloquear
            session_key = crypto_utils.unlock_vault_key(password, vault_key_content)

            # Si todo salio bien, manda a llamar main_app.py
            # para abrir la venta principal
            self.destroy()
            app = main_app.App(baul_path=str(self.baul_path), session_key=session_key)
            app.mainloop()

        except ValueError as e: # Captura "Contraseña incorrecta"
            self.status_label.configure(text=str(e), text_color="red")
            self.login_button.configure(state="normal")
            self.pass_entry.configure(state="normal")
            self.pass_entry.delete(0, "end")
        except FileNotFoundError:
            self.status_label.configure(text="ERROR >> No se encontró el archivo 'vault.key'.", text_color="red")
        except Exception as e:
            self.status_label.configure(text=f"ERROR >> {e}", text_color="red")
            self.login_button.configure(state="normal")
            self.pass_entry.configure(state="normal")