# -*- coding: utf-8 -*-

"""
Servicios de impresión.
Contiene toda la lógica relacionada con la impresión de archivos.
"""

import os
import subprocess
import tempfile
import threading
import time
import uuid
import win32api

from config import (
    NOMBRE_IMPRESORA, 
    RUTAS_SUMATRA, 
    TIMEOUT_POWERSHELL, 
    TIMEOUT_SUMATRA, 
    TIMEOUT_LIMPIEZA
)


class PrintService:
    """Servicio encargado de manejar todas las operaciones de impresión."""
    
    @staticmethod
    def guardar_archivo_temporal(archivo):
        """
        Guarda el archivo recibido en el directorio temporal del sistema.
        
        Args:
            archivo: Archivo recibido de la petición Flask
            
        Returns:
            str: Ruta del archivo temporal guardado
        """
        directorio_temporal = tempfile.gettempdir()
        nombre_base, extension = os.path.splitext(archivo.filename)
        extension = extension.lower()
        
        nombre_archivo_temporal = os.path.join(
            directorio_temporal, 
            f"etiqueta_{uuid.uuid4().hex}{extension}"
        )
        
        archivo.save(nombre_archivo_temporal)
        print(f"Archivo '{archivo.filename}' guardado temporalmente en: {nombre_archivo_temporal}")
        
        return nombre_archivo_temporal
    
    @staticmethod
    def imprimir_txt(ruta_archivo):
        """
        Imprime un archivo de texto plano usando PowerShell.
        
        Args:
            ruta_archivo (str): Ruta del archivo a imprimir
            
        Raises:
            Exception: Si hay error en la impresión
        """
        print("Intentando imprimir archivo TXT directamente...")
        comando_ps = f'Get-Content "{ruta_archivo}" | Out-Printer -Name "{NOMBRE_IMPRESORA}"'
        
        resultado = subprocess.run(
            ["powershell", "-Command", comando_ps],
            capture_output=True, 
            text=True, 
            timeout=TIMEOUT_POWERSHELL, 
            check=False
        )
        
        if resultado.returncode == 0:
            print("Archivo TXT enviado directamente a la impresora.")
        else:
            mensaje_error = resultado.stderr.strip()
            raise Exception(f"Error al imprimir con PowerShell: {mensaje_error}")
    
    @staticmethod
    def imprimir_pdf(ruta_archivo):
        """
        Imprime un archivo PDF usando SumatraPDF.
        
        Args:
            ruta_archivo (str): Ruta del archivo a imprimir
            
        Raises:
            Exception: Si hay error en la impresión o no se encuentra SumatraPDF
        """
        print("Intentando imprimir PDF con SumatraPDF...")
        
        sumatra_encontrado = False
        for ruta_sumatra in RUTAS_SUMATRA:
            ruta_expandida = os.path.expanduser(ruta_sumatra)
            if os.path.exists(ruta_expandida):
                print(f"SumatraPDF encontrado en: {ruta_expandida}")
                
                resultado = subprocess.run([
                    ruta_expandida,
                    "-print-to", NOMBRE_IMPRESORA,
                    "-silent",
                    ruta_archivo
                ], capture_output=True, text=True, timeout=TIMEOUT_SUMATRA, check=False)
                
                sumatra_encontrado = True
                if resultado.returncode == 0:
                    print("PDF enviado a la impresora usando SumatraPDF.")
                else:
                    print(f"Error con SumatraPDF: {resultado.stderr}")
                    raise Exception("SumatraPDF falló al intentar imprimir.")
                break
        
        if not sumatra_encontrado:
            raise Exception("SumatraPDF no encontrado en las rutas habituales. Por favor, instálalo.")
    
    @staticmethod
    def imprimir_con_respaldo(ruta_archivo):
        """
        Métodos de respaldo para impresión cuando fallan los métodos principales.
        
        Args:
            ruta_archivo (str): Ruta del archivo a imprimir
        """
        try:
            print("Intentando método de respaldo con win32api...")
            win32api.ShellExecute(0, "print", ruta_archivo, f'/d:"{NOMBRE_IMPRESORA}"', ".", 0)
            print("Archivo enviado a impresión usando el método de respaldo win32api.")
        except Exception as e2:
            print(f"ERROR con win32api: {str(e2)}")
            print("Último recurso: abriendo el archivo...")
            os.startfile(ruta_archivo)
    
    @staticmethod
    def programar_limpieza(ruta_archivo):
        """
        Programa la eliminación del archivo temporal en segundo plano.
        
        Args:
            ruta_archivo (str): Ruta del archivo temporal a eliminar
        """
        def limpiar_archivo():
            time.sleep(TIMEOUT_LIMPIEZA)
            try:
                os.remove(ruta_archivo)
                print(f"Archivo temporal '{ruta_archivo}' eliminado correctamente.")
            except Exception as e:
                print(f"ADVERTENCIA: No se pudo eliminar el archivo temporal. Error: {e}")
        
        threading.Thread(target=limpiar_archivo, daemon=True).start()
    
    @classmethod
    def procesar_impresion(cls, archivo):
        """
        Método principal que orquesta todo el proceso de impresión.
        
        Args:
            archivo: Archivo recibido de la petición Flask
            
        Returns:
            bool: True si la impresión fue exitosa
            
        Raises:
            Exception: Si hay errores en el proceso
        """
        # Guardar archivo temporal
        ruta_archivo = cls.guardar_archivo_temporal(archivo)
        
        try:
            # Determinar el método de impresión según la extensión
            _, extension = os.path.splitext(archivo.filename)
            extension = extension.lower()
            
            if extension == '.txt':
                cls.imprimir_txt(ruta_archivo)
            elif extension == '.pdf':
                cls.imprimir_pdf(ruta_archivo)
            
        except Exception as e:
            print(f"ERROR en método principal: {str(e)}")
            cls.imprimir_con_respaldo(ruta_archivo)
        
        finally:
            # Programar limpieza del archivo temporal
            cls.programar_limpieza(ruta_archivo)
        
        return True
