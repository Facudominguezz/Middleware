# -*- coding: utf-8 -*-

"""
Rutas de la aplicación Flask (blueprints).
Contiene todos los endpoints de la API.
"""
                                               #--------
from flask import Blueprint, request, Response, jsonify #<---- agregado por gabriel

from services import PrintService
from utils import ValidationUtils

# Crear blueprint para las rutas principales
main_bp = Blueprint('main', __name__)


@main_bp.route('/', methods=['GET'])
def estado_salud():
    """
    Endpoint de "health check" o verificación de estado.
    Permite comprobar rápidamente si el servidor está funcionando.
    Responde con un mensaje simple y un código de estado 200 OK.
    """
    return Response("Middleware de impresión activo", status=200)

## --------  METODO DE GET NUEVO GABRIEL LUJAN--------##

@main_bp.route('/printers', methods=['GET'])
def listar_impresoras():
    """
    Endpoint que devuelve una lista de las impresoras activas
    detectadas en el sistema.
    """
    try:
        # Reutilizamos la validación para asegurarnos de que estamos en Windows
        ValidationUtils.validar_sistema_operativo()

        # Llamamos al nuevo método del servicio de impresión
        impresoras = PrintService.obtener_impresoras_activas()

        # Devolvemos la lista en formato JSON
        return jsonify(impresoras), 200

    except Exception as e:
        print(f"ERROR en /printers: {str(e)}")
        return Response(f"Error: {str(e)}", status=500)

### ----- ---- ---- -----------------------------------------    

@main_bp.route('/print-pdf', methods=['POST'])
def imprimir_pdf():
    """
    Endpoint principal que recibe un archivo y lo manda a imprimir.
    """
    try:
        # 1. Verificación del sistema operativo
        ValidationUtils.validar_sistema_operativo()
        
        # 2. Depuración: Muestra los encabezados de la petición entrante
        print("\n--- ENCABEZADOS DE LA PETICIÓN ENTRANTE ---")
        print(request.headers)
        
        # 3. Validación de la petición y archivo
        archivo = ValidationUtils.validar_peticion(request)
        ValidationUtils.validar_archivo(archivo)
        
        # 4. Procesar impresión
        PrintService.procesar_impresion(archivo)
        
        # 5. Respuesta exitosa
        return Response("Archivo enviado a impresión", status=200)
        
    except Exception as e:
        # Manejo de errores
        print(f"ERROR: {str(e)}")
        
        # Determinar código de estado basado en el tipo de error
        if "no soportado" in str(e).lower():
            status_code = 415  # Unsupported Media Type
        elif "no se recibió" in str(e).lower() or "vacío" in str(e).lower():
            status_code = 400  # Bad Request
        elif "solo es compatible" in str(e).lower():
            status_code = 400  # Bad Request
        else:
            status_code = 500  # Internal Server Error
            
        return Response(f"Error: {str(e)}", status=status_code)

