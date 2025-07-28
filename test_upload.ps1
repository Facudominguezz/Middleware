# Script para enviar archivo PDF al middleware usando PowerShell 5.1
param(
    # Ruta del archivo PDF a enviar
    [string]$FilePath = "C:\Users\facu_\Downloads\Etiqueta (11).pdf"
)

# Detectar la IP pública automáticamente
try {
    Write-Host "Consultando la IP pública..."
    $publicIp = (Invoke-RestMethod -Uri 'https://api.ipify.org').Trim()
    Write-Host "IP pública detectada: $publicIp"
} catch {
    Write-Warning "No se pudo detectar la IP pública. Usando 'localhost' como alternativa."
    $publicIp = "localhost"
}
$ServerUrl = "http://${publicIp}:5000/print-pdf"

# Verificar que el archivo existe
if (-not (Test-Path $FilePath)) {
    Write-Error "El archivo no existe: $FilePath"
    exit 1
}

try {
    # Crear cliente HTTP
    Add-Type -AssemblyName System.Net.Http
    
    $httpClient = New-Object System.Net.Http.HttpClient
    $content = New-Object System.Net.Http.MultipartFormDataContent
    
    # Leer el archivo
    $fileBytes = [System.IO.File]::ReadAllBytes($FilePath)
    $fileName = [System.IO.Path]::GetFileName($FilePath)
    
    # Crear contenido del archivo
    $fileContent = New-Object System.Net.Http.ByteArrayContent -ArgumentList (,$fileBytes)
    $fileContent.Headers.ContentType = [System.Net.Http.Headers.MediaTypeHeaderValue]::Parse("application/pdf")
    
    # Agregar el archivo al form
    $content.Add($fileContent, "file", $fileName)
    
    # Enviar la petición
    Write-Host "Enviando archivo: $fileName"
    Write-Host "A servidor: $ServerUrl"
    
    $response = $httpClient.PostAsync($ServerUrl, $content).Result
    $responseContent = $response.Content.ReadAsStringAsync().Result
    
    Write-Host "Status Code: $($response.StatusCode)"
    Write-Host "Response: $responseContent"
    
    if ($response.IsSuccessStatusCode) {
        Write-Host "¡Archivo enviado exitosamente!" -ForegroundColor Green
    } else {
        Write-Host "Error al enviar archivo" -ForegroundColor Red
    }
    
} catch {
    Write-Error "Error: $($_.Exception.Message)"
} finally {
    if ($httpClient) {
        $httpClient.Dispose()
    }
}
