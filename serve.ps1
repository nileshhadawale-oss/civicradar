# CivicRadar - local static file server (no Node/Python required)
param(
  [int]$Port = 8080
)

$Root = $PSScriptRoot

$mime = @{
  '.html' = 'text/html; charset=utf-8'
  '.css'  = 'text/css; charset=utf-8'
  '.js'   = 'application/javascript; charset=utf-8'
  '.json' = 'application/json; charset=utf-8'
  '.svg'  = 'image/svg+xml'
  '.png'  = 'image/png'
  '.jpg'  = 'image/jpeg'
  '.jpeg' = 'image/jpeg'
  '.webp' = 'image/webp'
  '.ico'  = 'image/x-icon'
  '.txt'  = 'text/plain; charset=utf-8'
  '.mp3'  = 'audio/mpeg'
  '.wav'  = 'audio/wav'
  '.mp4'  = 'video/mp4'
}

function Start-CivicRadarListener([int]$TryPort) {
  $listener = New-Object System.Net.HttpListener
  $listener.Prefixes.Add("http://localhost:$TryPort/")
  $listener.Start()
  return $listener
}

$listener = $null
$startedPort = $null
$maxPort = $Port + 10

for ($try = $Port; $try -le $maxPort; $try++) {
  try {
    $listener = Start-CivicRadarListener $try
    $startedPort = $try
    break
  } catch [System.Net.HttpListenerException] {
    if ($try -eq $Port) {
      Write-Host ''
      Write-Host "  Port $Port is already in use." -ForegroundColor Yellow
      Write-Host '  Trying the next available port...' -ForegroundColor DarkGray
    }
    $listener = $null
  }
}

if (-not $listener) {
  Write-Host ''
  Write-Host "  Could not start server (ports ${Port}-${maxPort} busy)." -ForegroundColor Red
  Write-Host ''
  Write-Host '  Option 1: Open http://localhost:8080/ - a server may already be running.' -ForegroundColor Cyan
  Write-Host '  Option 2: Free port 8080, then run this script again:' -ForegroundColor Cyan
  Write-Host '            netstat -ano | findstr :8080' -ForegroundColor DarkGray
  Write-Host '            taskkill /PID [pid number] /F' -ForegroundColor DarkGray
  Write-Host ''
  exit 1
}

Write-Host ''
Write-Host "  CivicRadar is running at: http://localhost:$startedPort/" -ForegroundColor Green
Write-Host '  Press Ctrl+C to stop.' -ForegroundColor DarkGray
Write-Host ''

try {
  while ($listener.IsListening) {
    $context = $listener.GetContext()
    $request = $context.Request
    $response = $context.Response

    $rel = [Uri]::UnescapeDataString($request.Url.LocalPath.TrimStart('/'))
    if ([string]::IsNullOrWhiteSpace($rel)) { $rel = 'index.html' }

    $file = Join-Path $Root ($rel -replace '/', [IO.Path]::DirectorySeparatorChar)
    $file = [IO.Path]::GetFullPath($file)

    if (-not $file.StartsWith([IO.Path]::GetFullPath($Root), [StringComparison]::OrdinalIgnoreCase)) {
      $response.StatusCode = 403
      $response.Close()
      continue
    }

    if (Test-Path $file -PathType Leaf) {
      $bytes = [IO.File]::ReadAllBytes($file)
      $ext = [IO.Path]::GetExtension($file).ToLowerInvariant()
      $response.ContentType = if ($mime.ContainsKey($ext)) { $mime[$ext] } else { 'application/octet-stream' }
      $response.ContentLength64 = $bytes.Length
      $response.OutputStream.Write($bytes, 0, $bytes.Length)
      $line = '{0} {1} 200' -f $request.HttpMethod, $request.Url.LocalPath
      Write-Host $line -ForegroundColor DarkGray
    } else {
      $response.StatusCode = 404
      $line = '{0} {1} 404' -f $request.HttpMethod, $request.Url.LocalPath
      Write-Host $line -ForegroundColor Yellow
    }

    $response.Close()
  }
} finally {
  if ($listener -and $listener.IsListening) {
    $listener.Stop()
  }
  if ($listener) {
    $listener.Close()
  }
}
