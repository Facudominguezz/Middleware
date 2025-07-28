from flask import Flask, request, Response
import os
import platform
import win32api
import subprocess
import tempfile
import uuid
import socket

app = Flask(__name__)

# Cambiar por el nombre exacto de tu impresora en Windows
PRINTER_NAME = "Brother PT-P950NW"

def get_local_ip():
    """Obtiene la IP local automáticamente"""
    try:
        # Crear un socket para conectar a una dirección externa
        # Esto no envía datos, solo obtiene la IP local que se usaría
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            return local_ip
    except Exception:
        # Si falla, usar localhost como respaldo
        return "127.0.0.1"

@app.route('/', methods=['GET'])
def health():
    return Response("Middleware de impresión activo", status=200)

@app.route('/print-pdf', methods=['POST'])
def print_pdf():
    if platform.system() != "Windows":
        return Response("Solo compatible con Windows", status=400)

    try:
        if 'file' not in request.files:
            return Response("No se recibió archivo", status=400)
        
        file = request.files['file']
        if file.filename == '':
            return Response("Nombre de archivo vacío", status=400)
        
        ext = os.path.splitext(file.filename)[-1].lower()
        if ext not in ['.pdf', '.txt']:
            return Response("Tipo de archivo no soportado", status=415)
        
        # Guardar archivo temporalmente
        temp_dir = tempfile.gettempdir()
        temp_filename = os.path.join(temp_dir, f"etiqueta_{uuid.uuid4().hex}{ext}")
        file.save(temp_filename)

        # Enviar a impresora
        try:
            # Método 1: Para archivos TXT, usar Out-Printer directamente
            if ext == '.txt':
                # Primero verificar si la impresora soporta el tipo de archivo
                ps_command = f'Get-Content "{temp_filename}" | Out-Printer -Name "{PRINTER_NAME}"'
                result = subprocess.run([
                    "powershell", "-Command", ps_command
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    print(f"Archivo {ext.upper()} enviado directamente a impresora")
                else:
                    # Si falla con Out-Printer, la impresora no soporta este formato
                    error_msg = result.stderr.strip()
                    if "longitud no puede ser inferior a cero" in error_msg or "length" in error_msg.lower():
                        raise Exception(f"La impresora {PRINTER_NAME} no soporta archivos {ext.upper()}. Error: Formato no compatible.")
                    else:
                        raise Exception(f"Error imprimiendo {ext.upper()}: {result.stderr}")
            
            # Método 2: Para PDFs, usar SumatraPDF
            else:
                # Intentar con SumatraPDF primero
                sumatra_paths = [
                    os.path.expanduser("~\\AppData\\Local\\SumatraPDF\\SumatraPDF.exe"),
                    "C:\\Program Files\\SumatraPDF\\SumatraPDF.exe",
                    "C:\\Program Files (x86)\\SumatraPDF\\SumatraPDF.exe"
                ]
                
                sumatra_found = False
                for sumatra_path in sumatra_paths:
                    if os.path.exists(sumatra_path):
                        result = subprocess.run([
                            sumatra_path,
                            "-print-to", PRINTER_NAME,
                            "-silent",
                            temp_filename
                        ], capture_output=True, text=True, timeout=15)
                        
                        sumatra_found = True
                        if result.returncode == 0:
                            print("PDF enviado a impresora usando SumatraPDF")
                        else:
                            print(f"Error con SumatraPDF: {result.stderr}")
                            raise Exception("SumatraPDF falló")
                        break
                
                if not sumatra_found:
                    # Si SumatraPDF no está disponible, usar método alternativo
                    raise Exception("SumatraPDF no encontrado")
            
        except Exception as e:
            print(f"Error en método principal: {str(e)}")
            try:
                # Método de respaldo: usar win32api
                win32api.ShellExecute(0, "print", temp_filename, f'/d:"{PRINTER_NAME}"', ".", 0)
                print("Usando win32api como respaldo")
            except Exception as e2:
                print(f"Error con win32api: {str(e2)}")
                # Último recurso: abrir el archivo
                os.startfile(temp_filename)
                print("Abriendo archivo como último recurso")

        # Limpiar archivo temporal después de un breve delay
        def cleanup():
            import time
            time.sleep(5)  # Esperar 5 segundos antes de eliminar
            try:
                os.remove(temp_filename)
            except:
                pass
        
        import threading
        threading.Thread(target=cleanup, daemon=True).start()

        return Response(f"Archivo enviado a impresión", status=200)

    except Exception as e:
        return Response(f"Error: {str(e)}", status=500)

if __name__ == '__main__':
    local_ip = get_local_ip()
    print(f"🌐 Servidor iniciando en: http://{local_ip}:5000")
    print(f"📍 IP local detectada: {local_ip}")
    print(f"🖨️  Impresora configurada: {PRINTER_NAME}")
    print("📡 Servidor accesible solo desde la red local")
    
    app.run(host=local_ip, port=5000, debug=True)
