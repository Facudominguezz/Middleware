from flask import Flask, request, Response
import subprocess
import os
import platform

app = Flask(__name__)

# Configuración
PRINTER_USB = 'Brother PT-P950NW'  # nombre exacto de la impresora en el sistema
PRINTER_IP = '190.193.235.107'       # IP si es por red

@app.route('/', methods=['GET'])
def health_check():
    return Response("ZPL Print Server is running", status=200)

@app.route('/print', methods=['POST'])
def print_zpl():
    # Intentar obtener datos de diferentes formas
    if request.data:
        zpl = request.data.decode('utf-8')
    elif request.form.get('zpl'):
        zpl = request.form.get('zpl')
    elif request.json and 'zpl' in request.json:
        zpl = request.json['zpl']
    else:
        return Response("No ZPL data provided", status=400)
    
    # Validar que tenemos datos ZPL
    if not zpl or not zpl.strip():
        return Response("Empty ZPL data", status=400)

    try:
        if platform.system() == "Windows":
            # Crear archivo temporal con nombre único
            temp_file = 'temp_zpl_' + str(os.getpid()) + '.zpl'
            
            try:
                # Guardar temporalmente
                with open(temp_file, 'w') as f:
                    f.write(zpl)

                # Para impresora USB configurada por nombre
                subprocess.run(['notepad.exe', '/p', temp_file], check=True)

                # Alternativa directa si tienes puerto LPT/USB o red:
                # subprocess.run(['print', '/D:"%s"' % PRINTER_USB, temp_file], shell=True)
                
            finally:
                # Limpiar archivo temporal
                if os.path.exists(temp_file):
                    os.remove(temp_file)

        elif platform.system() == "Linux":
            # Enviar directamente por red a puerto 9100
            subprocess.run(['lp', '-d', PRINTER_USB], input=zpl.encode('utf-8'), check=True)

        return Response("OK", status=200)
    except Exception as e:
        return Response(f"Error printing: {str(e)}", status=500)

if __name__ == '__main__':
    app.run(port=5000)
