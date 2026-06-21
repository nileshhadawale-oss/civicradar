$ErrorActionPreference = 'Stop'
$appPath = 'C:\civicradar\js\app.js'
$supPath = 'C:\civicradar\tools\i18n-supplement.json'
if (-not (Test-Path $supPath)) { throw "Missing $supPath" }
$sup = Get-Content $supPath -Raw -Encoding UTF8 | ConvertFrom-Json
if (Test-Path 'C:\civicradar\tools\i18n-patch2.json') {
  $patch = Get-Content 'C:\civicradar\tools\i18n-patch2.json' -Raw -Encoding UTF8 | ConvertFrom-Json
  foreach ($loc in @('hi','mr','gu')) {
    foreach ($prop in $patch.$loc.PSObject.Properties) {
      $sup.$loc | Add-Member -NotePropertyName $prop.Name -NotePropertyValue $prop.Value -Force
    }
  }
}
$src = Get-Content $appPath -Raw -Encoding UTF8
$locales = @('hi', 'mr', 'gu')
$order = @('en', 'hi', 'mr', 'gu')

function Get-LocaleBlock([string]$text, [string]$loc) {
  $start = $text.IndexOf("    ${loc}: {")
  if ($start -lt 0) { throw "Locale block not found: $loc" }
  $nextIdx = @()
  foreach ($other in $order) {
    if ($other -eq $loc) { continue }
    $idx = $text.IndexOf("    ${other}: {")
    if ($idx -gt $start) { $nextIdx += $idx }
  }
  $end = ($nextIdx | Measure-Object -Minimum).Minimum
  if (-not $end) { $end = $text.IndexOf('  };', $start) }
  return @{ Start = $start; End = $end; Block = $text.Substring($start, $end - $start) }
}

function Escape-Js([string]$s) {
  return ($s -replace '\\', '\\\\' -replace "'", "\\'" -replace "`r", '' -replace "`n", '\\n')
}

$added = @{ hi = 0; mr = 0; gu = 0 }
$updated = @{ hi = 0; mr = 0; gu = 0 }

foreach ($loc in $locales) {
  $entries = $sup.$loc
  if (-not $entries) { continue }
  $info = Get-LocaleBlock $src $loc
  $block = $info.Block
  $insertLines = New-Object System.Collections.Generic.List[string]

  foreach ($prop in $entries.PSObject.Properties) {
    $key = $prop.Name
    $val = [string]$prop.Value
    $escaped = Escape-Js $val
    $line = "      '$key': '$escaped',"
    if ($block -match "(?m)^\s+'$([regex]::Escape($key))':") {
      $block = [regex]::Replace($block, "(?m)^\s+'$([regex]::Escape($key))':.*$", $line)
      $updated[$loc]++
    } else {
      $insertLines.Add($line) | Out-Null
      $added[$loc]++
    }
  }

  if ($insertLines.Count -gt 0) {
    $insertText = ($insertLines -join "`n") + "`n"
    $block = $block -replace '(?ms)\r?\n    \},\s*$', "`n$insertText    },"
  }

  $src = $src.Substring(0, $info.Start) + $block + $src.Substring($info.End)
}

Set-Content -Path $appPath -Value $src -Encoding UTF8 -NoNewline
Write-Output "Added: hi=$($added.hi) mr=$($added.mr) gu=$($added.gu)"
Write-Output "Updated: hi=$($updated.hi) mr=$($updated.mr) gu=$($updated.gu)"
