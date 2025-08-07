# -*- coding: utf-8 -*-

"""
Configuración de la aplicación Flask.
Contiene todas las constantes y configuraciones centralizadas.
"""

import socket

# --- CONFIGURACIÓN PRINCIPAL ---
# IMPORTANTE: Aquí debes poner el nombre exacto de tu impresora como aparece en Windows.
# Puedes encontrarlo en "Dispositivos e impresoras" o ejecutando en PowerShell: Get-Printer
NOMBRE_IMPRESORA = "PT-950NW"

# Configuración del servidor
HOST = "0.0.0.0"  # Se configurará dinámicamente
PORT = 5000
DEBUG = True

# Archivos soportados
EXTENSIONES_SOPORTADAS = ['.pdf', '.txt']

# Rutas de SumatraPDF
RUTAS_SUMATRA = [
    "~\\AppData\\Local\\SumatraPDF\\SumatraPDF.exe",
    "C:\\Program Files\\SumatraPDF\\SumatraPDF.exe",
    "C:\\Program Files (x86)\\SumatraPDF\\SumatraPDF.exe"
]

# Configuración de timeouts
TIMEOUT_POWERSHELL = 10
TIMEOUT_SUMATRA = 15
TIMEOUT_LIMPIEZA = 5


def obtener_ip_local():
    """
    Detecta automáticamente la dirección IP local de la máquina.
    Esto permite que el servidor sea accesible desde otros dispositivos en la misma red.
    """
    try:
        # Se crea un socket temporal para determinar la IP de la interfaz de red principal.
        # Se conecta a un servidor DNS público (de Google) para forzar al sistema operativo
        # a elegir la interfaz de red correcta, pero no se envía ningún dato.
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip_local = s.getsockname()[0]
            return ip_local
    except Exception as e:
        # Si por alguna razón no se puede detectar la IP (ej. no hay conexión a red),
        # se usa '127.0.0.1' (localhost) como valor predeterminado.
        print(f"ADVERTENCIA: No se pudo detectar la IP local. Usando '127.0.0.1'. Error: {e}")
        return "127.0.0.1"
