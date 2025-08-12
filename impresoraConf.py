import os
from config import NOMBRE_ARCHIVO_GUARDADO

_nombre_impresora_actual = "" # Variable interna para guardar el nombre en memoria.

def cargar_impresora_guardada():
    """Lee el archivo de guardado para establecer la impresora inicial."""
    global _nombre_impresora_actual
    try:
        if os.path.exists(NOMBRE_ARCHIVO_GUARDADO):
            with open(NOMBRE_ARCHIVO_GUARDADO, "r") as f:
                _nombre_impresora_actual = f.read().strip()
                print(f"INFO: Impresora cargada desde archivo: '{_nombre_impresora_actual}'")
        else:
            _nombre_impresora_actual = "Microsoft Print to PDF"
            print(f"INFO: No se encontró archivo de guardado. Usando impresora por defecto: '{_nombre_impresora_actual}'")
    except Exception as e:
        print(f"ERROR: No se pudo leer el archivo de guardado. {e}")
        _nombre_impresora_actual = "Microsoft Print to PDF"

def establecer_impresora_actual(nombre):
    """Actualiza la impresora en memoria y la guarda en el archivo."""
    global _nombre_impresora_actual
    _nombre_impresora_actual = nombre
    try:
        with open(NOMBRE_ARCHIVO_GUARDADO, "w") as f:
            f.write(nombre)
        print(f"INFO: Impresora '{nombre}' guardada para futuras sesiones.")
    except Exception as e:
        print(f"ERROR: No se pudo escribir en el archivo de guardado. {e}")

def obtener_impresora_actual():
    """Devuelve el nombre de la impresora en uso."""
    return _nombre_impresora_actual

# -- Se carga la impresora guardada al iniciar el programa --
cargar_impresora_guardada()