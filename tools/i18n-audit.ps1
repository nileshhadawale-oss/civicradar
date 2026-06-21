$src = Get-Content 'C:\civicradar\js\app.js' -Raw
$locales = @('en','hi','mr','gu')
$keys = @{}
for ($i = 0; $i -lt $locales.Count; $i++) {
  $loc = $locales[$i]
  $marker = "${loc}: {"
  $start = $src.IndexOf($marker)
  if ($i -lt $locales.Count - 1) {
    $next = $locales[$i + 1]
    $end = $src.IndexOf("${next}: {")
  } else {
    $end = $src.IndexOf('};', $start)
  }
  $block = $src.Substring($start, $end - $start)
  $keys[$loc] = [regex]::Matches($block, "'([^']+)':") | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique
}
"EN total: $($keys.en.Count)"
foreach ($loc in @('hi','mr','gu')) {
  $missing = $keys.en | Where-Object { $keys[$loc] -notcontains $_ }
  "$loc missing: $($missing.Count)"
  $missing | ForEach-Object { "  $_" }
}
