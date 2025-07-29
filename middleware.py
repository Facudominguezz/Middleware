# -*- coding: utf-8 -*-

"""
Middleware de impresión Flask.
Punto de entrada principal de la aplicación.
"""

from app import crear_app
from config import obtener_ip_local, NOMBRE_IMPRESORA, PORT

# --- PUNTO DE ENTRADA DE LA APLICACIÓN ---
# Este bloque solo se ejecuta cuando el script se corre directamente (ej. 'python middleware.py').
if __name__ == '__main__':
    # Crear la aplicación usando el factory pattern
    aplicacion = crear_app()
    
    # Se obtiene la IP local para que el servidor sea accesible en la red.
    ip_local = obtener_ip_local()
    
    # Se imprimen mensajes informativos en la consola al iniciar.
    print("--- INICIANDO MIDDLEWARE DE IMPRESIÓN ---")
    print(f"🌐 Servidor iniciando en: http://{ip_local}:{PORT}")
    print(f"📍 IP local detectada: {ip_local}")
    print(f"🖨️  Impresora configurada: '{NOMBRE_IMPRESORA}'")
    print("📡 Para detener el servidor, presiona CTRL+C")
    
    # Se inicia el servidor Flask.
    # host=ip_local -> Hace que el servidor sea visible en tu red local.
    # port=PORT -> El puerto en el que escuchará el servidor.
    # debug=True -> Activa el modo de depuración, que reinicia el servidor al detectar cambios en el código.
    aplicacion.run(host=ip_local, port=PORT, debug=True)

