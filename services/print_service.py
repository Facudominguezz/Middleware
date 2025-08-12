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

#Libreria Externas
import win32api
import wmi
import pythoncom

from config import (
    obtener_impresora_actual, 
    RUTAS_SUMATRA, 
    TIMEOUT_POWERSHELL, 
    TIMEOUT_SUMATRA, 
    TIMEOUT_LIMPIEZA,
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
        nombre_impresora = obtener_impresora_actual() # <-- OBTENER IMPRESORA ACTUAL
        print(f"Intentando imprimir archivo TXT en '{nombre_impresora}'...")
        comando_ps = f'Get-Content "{ruta_archivo}" | Out-Printer -Name "{nombre_impresora}"'
        
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
        nombre_impresora = obtener_impresora_actual() # <-- OBTENER IMPRESORA ACTUAL
        print(f"Intentando imprimir PDF con SumatraPDF en '{nombre_impresora}'...")
    
        sumatra_encontrado = False
        for ruta_sumatra in RUTAS_SUMATRA:
            ruta_expandida = os.path.expanduser(ruta_sumatra)
            if os.path.exists(ruta_expandida):
                print(f"SumatraPDF encontrado en: {ruta_expandida}")
                
                resultado = subprocess.run([
                    ruta_expandida,
                    "-print-to", nombre_impresora, # <-- Usar la variable
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
        
        if not sumatra_encontrado:
            raise Exception("SumatraPDF no encontrado en las rutas habituales. Por favor, instálalo.")
    
    @staticmethod
    def imprimir_con_respaldo(ruta_archivo):
        """
        Métodos de respaldo para impresión cuando fallan los métodos principales.
        
        Args:
            ruta_archivo (str): Ruta del archivo a imprimir
        """
        nombre_impresora = obtener_impresora_actual() # <-- OBTENER IMPRESORA ACTUAL
        try:
            print(f"Intentando método de respaldo con win32api en '{nombre_impresora}'...")
            win32api.ShellExecute(0, "print", ruta_archivo, f'/d:"{nombre_impresora}"', ".", 0)
            print("Archivo enviado a impresión usando el método de respaldo win32api.")
        except Exception as e2:
            print(f"ERROR con win32api: {str(e2)}")
            print("Último recurso: abriendo el archivo...")
            os.startfile(ruta_archivo)
    
    ###------------ Agregado Gabriel Lujan ---------------###
    @staticmethod
    def obtener_impresoras_activas():
        """
        Escanea el sistema en busca de impresoras que están listas para imprimir.
        """
        print("Escaneando impresoras listas en el sistema...")
        try:
            pythoncom.CoInitialize()
            c = wmi.WMI()
            impresoras_detalladas = []

            for printer in c.Win32_Printer():
                esta_en_linea = printer.WorkOffline is False
                estado_listo = printer.PrinterStatus == 3 or printer.PrinterStatus == 4

                if esta_en_linea and estado_listo:
                    port_name = printer.PortName
                    port = port_name
            
                    printer_info = {
                        "name": printer.Name,
                        "port": port
                    }
                    print(f"Impresora lista encontrada: {printer_info}")
                    impresoras_detalladas.append(printer_info)

            if not impresoras_detalladas:
                print("ADVERTENCIA: No se encontraron impresoras en estado 'En Línea' y 'Lista/Inactiva'.")

            return impresoras_detalladas
        
        except Exception as e:
            print(f"ERROR al escanear impresoras con WMI: {e}")
            return []
        finally:
            pythoncom.CoUninitialize()

     # --- MÉTODO NUEVO PARA ESTABLECER LA IMPRESORA PREDETERMINADA ---
    @staticmethod
    def establecer_impresora_predeterminada(nombre_impresora):
        """
        Establece una impresora como la predeterminada del sistema en Windows.
        """
        print(f"Intentando establecer '{nombre_impresora}' como predeterminada en Windows...")
        try:
            pythoncom.CoInitialize()
            c = wmi.WMI()
            impresora = c.Win32_Printer(Name=nombre_impresora)

            if not impresora:
                print(f"ERROR: No se encontró ninguna impresora con el nombre '{nombre_impresora}'.")
                return False

            impresora[0].SetDefaultPrinter()
            print(f"Impresora '{nombre_impresora}' establecida como predeterminada en Windows.")
            return True

        except Exception as e:
            print(f"ERROR al intentar establecer la impresora predeterminada: {e}")
            raise e
        finally:
            pythoncom.CoUninitialize()

    @staticmethod
    def programar_limpieza(ruta_archivo):
        """
        Programa la eliminación del archivo temporal en segundo plano.
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
        """
        ruta_archivo = cls.guardar_archivo_temporal(archivo)
        
        try:
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
            cls.programar_limpieza(ruta_archivo)
        
        return True
