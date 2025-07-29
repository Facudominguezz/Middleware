# Middleware de Impresión - Windows

Este middleware permite recibir archivos PDF y TXT a través de HTTP y enviarlos directamente a una impresora en Windows.

## 📁 Estructura del Proyecto

```
middleware/
├── middleware.py           # Punto de entrada principal
├── app.py                 # Factory de aplicación Flask
├── config.py              # Configuración centralizada
├── requirements.txt       # Dependencias del proyecto
├── routes/
│   ├── __init__.py
│   └── main.py           # Rutas/endpoints de la API
├── services/
│   ├── __init__.py
│   └── print_service.py  # Lógica de impresión
└── utils/
    ├── __init__.py
    └── validation.py     # Utilidades de validación
```

## 📝 Nota sobre IPs en ejemplos

En este documento verás referencias como:
- `tu-ip-local`: Tu IP local específica (ej: 192.168.1.100, 10.0.0.50, etc.)
- `tu-ip-publica`: Tu IP pública para acceso desde internet
- El middleware detecta automáticamente tu IP local al iniciarse

## 📋 Requisitos del Sistema

- **Sistema Operativo**: Windows 10/11
- **Python**: 3.7 o superior
- **PowerShell**: 5.1 o superior (incluido en Windows)
- **Impresora**: Compatible con Windows (probado con Brother PT-P950NW)

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/Facudominguezz/Middleware.git
cd Middleware
```

### 2. Crear entorno virtual de Python
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias de Python
```powershell
pip install -r requirements.txt
```

### 4. Instalar SumatraPDF (necesario para imprimir PDFs)
```powershell
winget install SumatraPDF.SumatraPDF
```

## ⚙️ Configuración

### 1. Configurar la impresora

Edita el archivo `config.py` y cambia el nombre de la impresora:

```python
# Cambiar por el nombre exacto de tu impresora en Windows
PRINTER_NAME = "Brother PT-P950NW"  # ← Cambiar aquí
```

Para encontrar el nombre exacto de tu impresora:
```powershell
Get-WmiObject -Class Win32_Printer | Select-Object Name
```

### 2. Verificar que la impresora funciona

Prueba imprimir un documento desde cualquier aplicación para asegurarte de que la impresora esté correctamente configurada.

## 🖥️ Uso

### Iniciar el servidor

```powershell
# Activar entorno virtual
.venv\Scripts\Activate.ps1

# Iniciar el middleware
python middleware.py
```

### 🌐 Configuración de IP del servidor

**El servidor detecta automáticamente tu IP local** y solo acepta conexiones desde la red local para mayor seguridad.

Cuando inicias el middleware verás algo como:
```
🌐 Servidor iniciando en: http://tu-ip-local:5000
📍 IP local detectada: tu-ip-local
🖨️  Impresora configurada: Brother PT-P950NW
📡 Servidor accesible solo desde la red local
```

**¿Cómo funciona?**
- El código detecta automáticamente tu IP local usando una conexión de prueba
- Solo acepta conexiones desde esa IP específica
- Es más seguro que `0.0.0.0` (que acepta desde cualquier IP)
- Se actualiza automáticamente si cambias de red

### Encontrar tu IP actual:

Si necesitas saber tu IP actual para usarla desde otra computadora:

```powershell
# Ver la IP que está usando el middleware
# (aparece al iniciar el servidor)

# O verificar manualmente:
ipconfig | findstr "IPv4"
```

### Configuraciones alternativas de IP:

Si necesitas cambiar el comportamiento, puedes modificar `middleware.py`:

```python
# Detección automática (configuración actual)
local_ip = get_local_ip()
app.run(host=local_ip, port=5000, debug=True)

# Solo localhost (máxima seguridad)
app.run(host='127.0.0.1', port=5000, debug=True)

# IP específica manual
app.run(host='tu-ip-local', port=5000, debug=True)

# Cualquier IP (menos seguro)
app.run(host='0.0.0.0', port=5000, debug=True)
```

### Verificar que funciona

```powershell
# Probar endpoint de salud (usar tu IP local)
Invoke-RestMethod -Uri "http://tu-ip-local:5000/" -Method GET
```

Debería responder: `"Middleware de impresión activo"`

## 📤 Enviar archivos para imprimir

### Opción 1: Usar el script de PowerShell incluido

```powershell
# El script detecta automáticamente la IP del servidor
PowerShell -ExecutionPolicy Bypass -File "test_upload.ps1"

# O especificar manualmente (si sabes la IP)
PowerShell -ExecutionPolicy Bypass -File "test_upload.ps1" -FilePath "archivo.pdf" -ServerUrl "http://tu-ip-local:5000/print-pdf"
```

**💡 Tip**: El script usa la IP por defecto del servidor. La IP se detecta automáticamente al iniciar el middleware.

**📝 Personalizar el script**: Si necesitas cambiar la IP por defecto en `test_upload.ps1`, edita la línea:
```powershell
[string]$ServerUrl = "http://tu-ip-local:5000/print-pdf"  # Cambiar por tu IP actual
```

### Opción 2: Usar curl (si está disponible)

```bash
curl -X POST -F "file=@archivo.pdf" http://tu-ip-local:5000/print-pdf
```

### Opción 3: Usar PowerShell manualmente

Para PowerShell 7+ (PowerShell Core):
```powershell
$response = Invoke-WebRequest -Uri "http://190.193.235.6:5000/print-pdf" -Method POST -Form @{
    file = Get-Item "C:\ruta\archivo.pdf"
}
Write-Host $response.Content
```

## 📁 Tipos de archivo soportados

| Extensión | Método de impresión | Descripción | Notas |
|-----------|-------------------|-------------|-------|
| `.pdf` | SumatraPDF | Documentos PDF | Requiere SumatraPDF instalado |
| `.txt` | Out-Printer directo | Archivos de texto plano | Envío directo sin procesamiento |

**Importante**: 
- Los archivos **PDF** se procesan a través de SumatraPDF para convertirlos a formato de impresión
- Los archivos **TXT** se envían tal como están a la impresora (si es compatible)

## ❌ Formatos NO soportados

### ZPL (Zebra Programming Language)

**Los archivos ZPL NO son compatibles** con la impresora Brother PT-P950NW por las siguientes razones:

1. **Incompatibilidad de lenguajes de comando:**
   - **ZPL** es un lenguaje de programación específico para impresoras **Zebra**
   - **Brother PT-P950NW** utiliza el lenguaje de comandos **P-touch Template** y **Brother Command**
   - Son protocolos completamente diferentes e incompatibles

2. **Evidencia técnica:**
   ```powershell
   # Prueba realizada durante desarrollo:
   PS C:\> Get-Content "test_label.zpl" | Out-Printer -Name "Brother PT-P950NW"
   
   # Resultado:
   out-lineoutput : La longitud no puede ser inferior a cero.
   Nombre del parámetro: length
   ```

3. **Documentación oficial:**
   - **Brother PT-P950NW**: Impresora de etiquetas que utiliza tecnología P-touch
   - **Formatos soportados por Brother**: .lbx, .lbz (P-touch Template), comandos ESC/P
   - **ZPL**: Exclusivo para impresoras Zebra (ZT, ZD, GK, GX series)

4. **Alternativas recomendadas:**
   - Usar **Brother P-touch Editor** para crear etiquetas
   - Convertir diseños a **PDF** antes de imprimir
   - Utilizar **comandos Brother** específicos si se requiere programación directa

**Fuentes:**
- [Brother PT-P950NW Manual](https://support.brother.com/g/b/manualtop.aspx?c=us&lang=en&prod=lp950nwus)
- [Zebra ZPL Documentation](https://www.zebra.com/us/en/support-downloads/knowledge-articles/zpl-programming-guide.html)
- Pruebas técnicas realizadas durante el desarrollo de este middleware

## 🔧 Solución de problemas

### Error: "No se encuentra ningún parámetro que coincida con el nombre del parámetro 'Form'"

**Causa**: Estás usando PowerShell 5.1 (Windows PowerShell)  
**Solución**: Usa el script `test_upload.ps1` incluido en el proyecto

### Error: "Uno de los dispositivos conectados al sistema no funciona"

**Causa**: Problema con la configuración de la impresora  
**Soluciones**:
1. Verificar que la impresora esté encendida y conectada
2. Verificar el nombre exacto de la impresora:
   ```powershell
   Get-WmiObject -Class Win32_Printer | Where-Object {$_.WorkOffline -eq $false} | Select-Object Name, PrinterStatus
   ```
3. Actualizar el `PRINTER_NAME` en `middleware.py`

### Error: "SumatraPDF no encontrado"

**Causa**: SumatraPDF no está instalado  
**Solución**:
```powershell
winget install SumatraPDF.SumatraPDF
```

### El archivo se abre pero no se imprime

**Causa**: Configuración de aplicación predeterminada  
**Solución**: El middleware debería usar SumatraPDF automáticamente. Si el problema persiste, verificar la instalación de SumatraPDF.

### Los archivos ZPL no se imprimen correctamente

**Respuesta**: **Los archivos ZPL NO son compatibles** con la impresora Brother PT-P950NW.

**Razón técnica**: ZPL (Zebra Programming Language) es un lenguaje específico para impresoras Zebra. La Brother PT-P950NW utiliza comandos P-touch Template completamente diferentes.

**Soluciones alternativas**:
1. Convertir el diseño de etiqueta a PDF usando herramientas de diseño
2. Usar Brother P-touch Editor para crear etiquetas nativas
3. Utilizar una impresora Zebra si se requiere soporte ZPL nativo

**Prueba técnica realizada**:
```powershell
Get-Content "archivo.zpl" | Out-Printer -Name "Brother PT-P950NW"
# Error: La longitud no puede ser inferior a cero
```

## 🌐 Configuración de red

### Para uso local (configuración actual)

El servidor detecta automáticamente tu IP local y solo acepta conexiones desde la red local. Esto es seguro y recomendado para uso interno.

### Para uso desde internet (Odoo, sistemas externos)

Si necesitas que Odoo u otros sistemas externos accedan al middleware desde internet, tienes estas opciones:

#### **Opción 1: Cambiar a todas las interfaces**
Modifica `middleware.py`:
```python
# Cambiar esta línea:
app.run(host=local_ip, port=5000, debug=True)

# Por esta:
app.run(host='0.0.0.0', port=5000, debug=True)
```

Luego configura **port forwarding** en tu router:
- Puerto externo: 5000 → IP interna: tu-ip-local:5000
- Odoo podrá enviar archivos a: `http://tu-ip-publica:5000/print-pdf`

#### **Opción 2: Usar túnel seguro (recomendado)**
```powershell
# Instalar ngrok
winget install ngrok.ngrok

# Crear túnel (requiere cuenta gratuita)
ngrok http 5000
```

Ngrok te dará una URL pública temporal como: `https://abc123.ngrok.io`
Odoo puede usar: `https://abc123.ngrok.io/print-pdf`

#### **⚠️ Consideraciones de seguridad para internet:**

Si expones el middleware a internet, considera agregar:

1. **Autenticación por token**:
```python
@app.before_request
def check_auth():
    token = request.headers.get('Authorization')
    if token != 'Bearer tu-token-secreto':
        return Response('No autorizado', status=401)
```

2. **Rate limiting** para evitar spam

3. **HTTPS** en lugar de HTTP

4. **Validación de archivos** más estricta

### Permitir conexiones externas

El servidor por defecto está configurado para IP local específica. Para cambiar el comportamiento:

```python
# IP local específica (configuración actual)
local_ip = get_local_ip()
app.run(host=local_ip, port=5000, debug=True)

# Solo localhost (máxima seguridad)
app.run(host='127.0.0.1', port=5000, debug=True)

# Todas las interfaces (para acceso desde internet)
app.run(host='0.0.0.0', port=5000, debug=True)
```
### Firewall de Windows

Si necesitas acceso desde otras computadoras:

```powershell
# Permitir el puerto 5000
New-NetFirewallRule -DisplayName "Middleware Impresión" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
```

## 📋 API Reference

### GET /
**Descripción**: Endpoint de salud  
**Respuesta**: `"Middleware de impresión activo"`

### POST /print-pdf
**Descripción**: Enviar archivo para imprimir  
**Parámetros**:
- `file`: Archivo a imprimir (PDF, ZPL, TXT)

**Respuestas**:
- `200`: Archivo enviado correctamente
- `400`: Error en la solicitud (archivo faltante, SO no compatible)
- `415`: Tipo de archivo no soportado
- `500`: Error interno del servidor

**Ejemplo de respuesta exitosa**:
```
Archivo enviado a impresión
```

## 🔄 Desarrollo

### Modo debug

El servidor incluye modo debug por defecto. Para producción:

```python
app.run(host='0.0.0.0', port=5000, debug=False)
```

### Logs

Los logs aparecen en la consola donde se ejecuta el servidor. Para más detalle, verificar las salidas `print()` en el código.

## 📝 Notas adicionales

- Los archivos temporales se eliminan automáticamente después de 5 segundos
- El middleware está optimizado para Windows únicamente
- Se recomienda usar en redes locales por seguridad

## 🆘 Soporte

Si encuentras problemas:

1. Verificar que todos los requisitos estén instalados
2. Comprobar los logs del servidor
3. Probar imprimir manualmente desde Windows
4. Verificar conectividad de red si usas IPs remotas

---

**Desarrollado para Windows - Probado con Brother PT-P950NW**
