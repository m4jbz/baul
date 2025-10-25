import os
import subprocess
import customtkinter
import pywinstyles
import sys
from pathlib import Path

ICON_FILE = "assets/icon.ico" 

try:
    ctk_path = Path(customtkinter.__file__).parent / "assets"
    pws_path = Path(pywinstyles.__file__).parent

    command = [
        'pyinstaller',
        '--noconfirm',
        '--onedir',
        '--windowed',
        '--name=BaulSeguro',
        f'--icon={ICON_FILE}',
        f'--add-data={ctk_path};customtkinter/assets',
        f'--add-data={pws_path};pywinstyles',
        '--hidden-import=watchdog.observers.api',
        'src/run.py'
    ]

    print(" ".join(command)) # Mostrar el comando a ejecutar
    subprocess.run(" ".join(command), shell=True, check=True) # Ejecutarlo

    print("\n" + "="*50)
    print("Compilacion terminada.")
    print("="*50)

except subprocess.CalledProcessError as e:
    print("\n" + "="*50)
    print("ERROR >> PyInstaller falló.")
    if f"'{ICON_FILE}'" in str(e):
        print(f"ERROR >> No se pudo encontrar el archivo de ícono '{ICON_FILE}'.")
    else:
        print(f"ERROR >> {e}")
    print("="*50)
except Exception as e:
    print(f"\nERROR >> {e}")