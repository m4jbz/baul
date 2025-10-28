import customtkinter as ctk
import os, time
from tkinter import messagebox
from pathlib import Path
from tkinter import filedialog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from cryptography.fernet import Fernet, InvalidToken
from tkinterdnd2 import DND_FILES, TkinterDnD 

# Como se va a ver la GUI
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Clase para el arbol de archivos, hereda de la clase padre: CTkScrollableFrame
# Ya que se podran tener varias carpetas y archivos, asi que es necesario que se
# pueda scrollear
class FileTreeView(ctk.CTkScrollableFrame):
    def __init__(self, master, path, fernet: Fernet, **kwargs):
        super().__init__(master, **kwargs)

        self.path = path
        self.fernet = fernet # La llave de sesión descifrada

        # Inicialización de:
        # checkboxes: las que se van a seleccionar
        # folder_children: subcarpetas
        # real_path_map: 
        self.checkboxes = {}
        self.folder_children = {}
        self.real_path_map = {}

        # Llenar el árbol
        self.populate_tree(self.path, 0)

    # Al activar o desactivar un checkbox
    def on_checkbox_toggle(self, display_path):
        is_checked = self.checkboxes[display_path].get()
        # Actualiza las subcarpetas si una carpeta padre fue seleccionada
        if display_path in self.folder_children:
            self.update_children_state(display_path, is_checked)

    # Se encarga de la actualizacion de estado de las subcarpetas de una carpeta padre
    def update_children_state(self, parent_display_path, state):
        if parent_display_path in self.folder_children:
            for child_display_path in self.folder_children[parent_display_path]:
                if state == 1:
                    self.checkboxes[child_display_path].select()
                else:
                    self.checkboxes[child_display_path].deselect()
                self.update_children_state(child_display_path, state)

    # Llena el árbol
    # Toma los datos: self (el objeto mismo), current_path: el directorio real y actual
    # row: el numero de fila, indent: la sangría para poner los archivos
    # parent_display_path: el nombre legible de la carpeta/directorio
    def populate_tree(self, current_path, row, indent=0, parent_display_path=""):
        try:
            # Se leen los nombres de archivo cifrados del disco, se ordenan con sorted()
            # para una mejor presentación
            items = sorted(os.listdir(current_path))
        except (FileNotFoundError, PermissionError) as e:
            print(f"Error al acceder a {current_path}: {e}")
            return row

        # self.folder_children es un diccionario con las rutas guardadas de forma 
        # de arbol jerarquico, empezando con: ""
        # Entonces este if pregunta si la carpeta padre en la que se esta trabajando
        # osea parent_display_path no esta dentro del diccionario, si no lo esta se
        # crea una lista vacia con el nombre de dicha ruta, si ya esta dentro del
        # diccionario, sigue el programa hasta que esa ruta/carpeta ya sea haya "completado"
        if parent_display_path not in self.folder_children:
            self.folder_children[parent_display_path] = []

        # Listas de los directorios y los archivos
        dirs = [item for item in items if os.path.isdir(os.path.join(current_path, item))]
        files = [item for item in items if not os.path.isdir(os.path.join(current_path, item)) and item.endswith(".enc")] # Para todos los archivos que terminan en .enc

        # Todo junto
        all_items = dirs + files
        # Esta lista se modificara con cada iteracion del ciclo
        # Se encarga de obtener las subcarpetas y sus archivos
        # Al final se guardaran en self.folder_children
        current_display_children = []

        # Ciclo que pasa por todas las carpetas y archivos
        for item in all_items:
            real_item_path = os.path.join(current_path, item)
            # Verifica si es un directorio/carpeta
            is_dir = os.path.isdir(real_item_path)

            # Si es la carpeta .credentials pasa a la siguiente iteracion, ya que
            # no se piensa mostrar dicha carpeta
            if item == ".credentials":
                continue

            display_name = ""

            if is_dir:
                icon = "📁"
                try:
                    # Se desencripta el nombre de la carpeta
                    encrypted_name_hex = item
                    decrypted_name_bytes = self.fernet.decrypt(bytes.fromhex(encrypted_name_hex))
                    # Nombre que se mostrara en la GUI
                    display_name = decrypted_name_bytes.decode('utf-8')
                except (InvalidToken, ValueError, TypeError):
                    display_name = f"¡Carpeta corrupta! ({item[:10]}...)"
                except Exception:
                    display_name = f"¡Error al leer! ({item[:10]}...)"
            else:
                icon = "📄"
                try:
                    # Se desencripta el nombre del archivo para mostrarlo
                    encrypted_name_hex = item.replace(".enc", "") # Se le quita el .enc
                    decrypted_name_bytes = self.fernet.decrypt(bytes.fromhex(encrypted_name_hex)) 
                    # Nombre que se mostrara en la GUI
                    display_name = decrypted_name_bytes.decode('utf-8')
                except (InvalidToken, ValueError, TypeError):
                    display_name = f"¡Archivo corrupto! ({item[:10]}...)"
                except Exception:
                    display_name = f"¡Error al leer! ({item[:10]}...)"

            # Se usa el 'display_name' para el arbol y los diccionarios
            # El 'display_path' es la ruta visual, no la real
            display_path = os.path.join(parent_display_path, display_name)
            current_display_children.append(display_path)

            cb = ctk.CTkCheckBox(self, text=f"{icon} {display_name}", 
                                 command=lambda p=display_path: self.on_checkbox_toggle(p))
            cb.grid(row=row, column=0, sticky="w", padx=(indent * 20, 0), pady=2)

            self.checkboxes[display_path] = cb
            # Se guarda el mapeo: "Ruta/Visual/Archivo.txt" -> "E:/Baul/...hex...enc"
            self.real_path_map[display_path] = real_item_path 
            # La fila aumenta uno para la siguiente iteracion y la sangría se mas grande
            # osea se dibuje más hacía la derecha
            row += 1

            if is_dir:
                row = self.populate_tree(real_item_path, row, indent + 1, parent_display_path=display_path)

        if parent_display_path:
            self.folder_children[parent_display_path] = current_display_children

        return row

    def get_checked_items(self):
        checked_real_paths = []
        for display_path, checkbox in self.checkboxes.items():
            if checkbox.get() == 1:
                # Se añade la ruta real cifrada, no la visual
                checked_real_paths.append(self.real_path_map[display_path])
        return checked_real_paths

    def refresh(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.checkboxes = {}
        self.folder_children = {}
        self.real_path_map = {}
        self.populate_tree(self.path, 0, parent_display_path="")

# Clase para actualizar automaticamente el arbol de archivos
# Utiliza un hilo de procesamiento separado para no congelar
# la interfaz
class ChangeHandler(FileSystemEventHandler):
    def __init__(self, app_instance):
        self.app = app_instance
        self.last_event_time = 0 # Inicia el cronometro
        self.debounce_time = 0.5 # 500 ms

    # Verifica si ha pasado el debounce_time,
    # si ya paso se reinicia el cronometro
    def on_any_event(self, event):
        current_time = time.time()
        if current_time - self.last_event_time > self.debounce_time:
            self.last_event_time = current_time
            # Se asegura que la ventana principal siga existiendo
            # para despues "decirle" a la ventana principal que en 100ms
            # ejecute la función app.tree_view_.refresh en su propio
            # hilo
            if self.app.winfo_exists():
                self.app.after(100, self.app.tree_view.refresh)

class App(ctk.CTk, TkinterDnD.Tk):
    def __init__(self, baul_path, session_key: Fernet):
        super().__init__()
        
        # Drag and Drop, Arrastra y Suelta, se inicializa la librería para poder usar DnD
        try:
            self.TkdndVersion = TkinterDnD._require(self)
        except Exception as e:
            messagebox.showerror("Error de DND", f"No se pudo inicializar la librería Drag and Drop (TkinterDnD).\n{e}")
            exit(1)

        self.baul_path = baul_path
        self.fernet = session_key # La llave de sesión descifrada

        if not os.path.exists(self.baul_path):
            messagebox.showerror("Error", "No se encontró la carpeta 'Baul'.")
            exit(1)

        self.title("Baúl Seguro")
        self.minsize(800, 600)

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        file_tree = ctk.CTkFrame(self)
        file_tree.grid(row=0, column=0, pady=10, sticky="NSEW")
        file_tree.grid_rowconfigure(1, weight=1)
        file_tree.grid_columnconfigure(0, weight=1)

        # Arbol jerarquico de archivos
        self.tree_view = FileTreeView(file_tree, path=self.baul_path, fernet=self.fernet)
        self.tree_view.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        drop_area = ctk.CTkFrame(self)
        drop_area.grid(row=0, column=1, padx=10, pady=10, sticky="NSEW")

        # Botón para enviar los archivos a una ruta especifica
        goto_button = ctk.CTkButton(self, text="Enviar a", fg_color="green", hover=True, command=self.button_event)
        goto_button.grid(row=1, column=1, sticky="SE", padx=10, pady=10)

        # Area de DnD
        label = ctk.CTkLabel(drop_area, text="Arrastra y suelta archivos aquí\n(para CIFRAR y guardar)", font=("Arial", 16))
        label.pack(expand=True)

        # Se encarga de actualizar el arbol de archivos cada cierto tiempo
        self.observer = Observer()
        event_handler = ChangeHandler(self)
        self.observer.schedule(event_handler, self.baul_path, recursive=True)
        self.observer.start()

        drop_area.drop_target_register(DND_FILES)
        drop_area.dnd_bind('<<Drop>>', self.on_drop_dnd_event)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_drop_dnd_event(self, event):
        files_dragged = self.tk.splitlist(event.data)
        
        # Pasamos la lista de archivos arrastrados a la USB
        self.on_drop_to_usb(files_dragged)

    def on_drop_to_usb(self, files_dragged):
        # Si no hay lista retornar
        if not files_dragged:
            return

        # Se intenta encriptar y copiar los archivos a la USB
        try:
            for item_path_str in files_dragged:
                item_path = Path(item_path_str)
                self.encrypt_and_copy_item(item_path, self.baul_path)

            messagebox.showinfo("Éxito", f"{len(files_dragged)} elemento(s) cifrados y copiados a la USB.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al cifrar y copiar:\n{e}")

    # Se encarga de la encripción y copiado de los archivos
    def encrypt_and_copy_item(self, source_path: Path, destination_folder: str):
        if source_path.is_dir():
            # Si es una carpeta, ciframos su nombre y la creamos
            encrypted_name_hex = self.fernet.encrypt(source_path.name.encode('utf-8')).hex()
            new_dest_folder = os.path.join(destination_folder, encrypted_name_hex) # Sin .enc
            os.makedirs(new_dest_folder, exist_ok=True)

            # Recursión: Ciframos todo el contenido de esta carpeta
            for sub_item in source_path.iterdir():
                self.encrypt_and_copy_item(sub_item, new_dest_folder)

        elif source_path.is_file():
            # Si es un archivo, ciframos el nombre y el contenido
            # Cifrar nombre
            encrypted_name_hex = self.fernet.encrypt(source_path.name.encode('utf-8')).hex()
            destination_path = os.path.join(destination_folder, encrypted_name_hex + ".enc")

            # Fernet carga todo en RAM. Para archivos > 1GB esto puede ser lento.
            with open(source_path, 'rb') as f:
                data = f.read()

            encrypted_data = self.fernet.encrypt(data)

            with open(destination_path, 'wb') as f:
                f.write(encrypted_data)

    # Esta función ahora DESCIFRA todo lo seleccionado de las checkboxes
    def button_event(self):
        # get_checked_items() ya nos da las rutas reales (cifradas)
        checked_items_real_paths = self.tree_view.get_checked_items()

        # Si no se selecciono nada, mostrar un warning
        if not checked_items_real_paths:
            messagebox.showwarning("Nada seleccionado", "Primero selecciona los archivos que quieres copiar.")
            return

        # Se filtra la lista para evitar copias duplicadas
        # Esto sirve al momento de copiar archivos dentro de carpetas o carpetas enteras
        # evitar doble copiado
        top_level_items = []
        checked_set = set(checked_items_real_paths)
        for item_path in checked_items_real_paths:
            parent = os.path.dirname(item_path)
            if parent not in checked_set:
                 # Se añade si su padre no está en la lista
                if item_path != self.baul_path:
                    top_level_items.append(item_path)

        if not top_level_items:
            # Esto puede pasar si solo se seleccionó la raíz o nada
            return

        # Dialog de windows para escoger una carpeta
        destination_folder = filedialog.askdirectory(title="Selecciona una carpeta de destino")

        if destination_folder:
            # Intenta decriptar y copiar los archivos de la USB a la ruta
            try:
                for item_path_str in top_level_items:
                    self.decrypt_and_copy_item(Path(item_path_str), destination_folder)

                messagebox.showinfo("Éxito", f"{len(top_level_items)} elemento(s) descifrados y copiados a:\n{destination_folder}")
            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error al descifrar y copiar:\n{e}")

    # Se encarga de decriptar y mandar los archivos de la USB a la ruta/carpeta dada
    def decrypt_and_copy_item(self, source_path: Path, destination_folder: str):
        if source_path.is_dir():
            # Si es una carpeta, desciframos su nombre
            try:
                encrypted_name_hex = source_path.name
                decrypted_name = self.fernet.decrypt(bytes.fromhex(encrypted_name_hex)).decode('utf-8')
                new_dest_folder = os.path.join(destination_folder, decrypted_name)
                os.makedirs(new_dest_folder, exist_ok=True)
            except Exception as e:
                print(f"No se pudo descifrar el nombre de la carpeta {source_path.name}: {e}")
                messagebox.showwarning("Error de nombre", f"No se pudo descifrar el nombre de la carpeta {source_path.name}. Se omitirá.")
                return

            # Recursión: Desciframos todo su contenido
            for sub_item in source_path.iterdir():
                self.decrypt_and_copy_item(sub_item, new_dest_folder)

        elif source_path.is_file() and source_path.name.endswith(".enc"):
            # Si es un archivo .enc
            # Descifrar nombre
            try:
                encrypted_name_hex = source_path.name.replace(".enc", "")
                decrypted_name = self.fernet.decrypt(bytes.fromhex(encrypted_name_hex)).decode('utf-8')
                destination_path = os.path.join(destination_folder, decrypted_name)
            except Exception as e:
                print(f"No se pudo descifrar el nombre {source_path.name}: {e}")
                messagebox.showwarning("Error de nombre", f"No se pudo descifrar el nombre del archivo {source_path.name}. Se omitirá.")
                return

            # Descifrar contenido
            try:
                with open(source_path, 'rb') as f:
                    encrypted_data = f.read()

                data = self.fernet.decrypt(encrypted_data)

                with open(destination_path, 'wb') as f:
                    f.write(data)
            except InvalidToken:
                messagebox.showerror("Error", f"Error de llave al descifrar {decrypted_name}. ¿Archivo corrupto?")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo descifrar el contenido de {decrypted_name}: {e}")

    def on_closing(self):
        self.observer.stop()
        self.observer.join()
        self.destroy()