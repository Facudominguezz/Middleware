# -*- coding: utf-8 -*-

"""
Utilidades de validación.
Contiene funciones para validar archivos y peticiones.
"""

import os
import platform

from config import EXTENSIONES_SOPORTADAS


class ValidationUtils:
    """Utilidades para validación de archivos y sistema."""
    
    @staticmethod
    def validar_sistema_operativo():
        """
        Valida que el sistema operativo sea Windows.
        
        Returns:
            bool: True si es Windows
            
        Raises:
            Exception: Si no es Windows
        """
        if platform.system() != "Windows":
            raise Exception("Este middleware solo es compatible con Windows.")
        return True
    
    @staticmethod
    def validar_archivo(archivo):
        """
        Valida que el archivo recibido sea válido y tenga una extensión soportada.
        
        Args:
            archivo: Archivo recibido de la petición Flask
            
        Returns:
            bool: True si el archivo es válido
            
        Raises:
            Exception: Si el archivo no es válido
        """
        # Validar que el archivo existe
        if not archivo:
            raise Exception("No se recibió archivo. Asegúrate de que el campo del formulario se llame 'file'.")
        
        # Validar nombre de archivo
        if archivo.filename == '':
            raise Exception("Nombre de archivo vacío.")
        
        # Validar extensión
        _, extension = os.path.splitext(archivo.filename)
        extension = extension.lower()
        
        if extension not in EXTENSIONES_SOPORTADAS:
            raise Exception(f"Tipo de archivo no soportado: '{extension}'. Solo se admiten {', '.join(EXTENSIONES_SOPORTADAS)}.")
        
        return True
    
    @staticmethod
    def validar_peticion(request):
        """
        Valida que la petición HTTP contenga un archivo.
        
        Args:
            request: Objeto request de Flask
            
        Returns:
            file: El archivo de la petición
            
        Raises:
            Exception: Si la petición no es válida
        """
        if 'file' not in request.files:
            raise Exception("La petición no contiene el campo 'file'.")
        
        return request.files['file']
