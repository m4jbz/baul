# Proyecto Tecnologías e Interfaces de Computadoras

El programa empieza con src/run.py el cual maneja las operaciones con USB,
checa los siguientes casos:

+ NO hay USB: Manda un mensaje de error diciendole al usuario que inserte por lo menos una USB.
+ SI hay UNA SOLA USB: El programa pasa a la seccion de login o setup, dependiendo si Baul/ existe dentro de esa USB.
+ SI hay MÁS DE UNA USB: Muestra un pequeño recuadro para esocoger cual USB es la que debería usarse.

Después de tener la USB ya seleccionada, se verifica si contiene la carpeta Baul/ y el archivo .credentials/vault.key dentro de la USB.
Si existe se pasa a src/login_gui.py, si no existe se pasa a src/setup_gui.py el cual crea la carpeta y pide una contraseña maestra, la
cual se guardara en un archivo.key encriptado. Una vez pasado todo tanto el setup como el login dependiendo del caso se muestra la ventana
principal src/main_app.py, la cual tiene el file tree con la sección para agarrar y soltar archivos del explorador de archivos de windows.

## Documentación

[DOCUMENTATION.md](docs/DOCUMENTATION.md)
