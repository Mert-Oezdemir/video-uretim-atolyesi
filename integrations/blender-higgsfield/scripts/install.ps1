param(
  [ValidateSet('official','community')]
  [string]$Backend = 'official'
)
$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'Git kur: https://git-scm.com/downloads' }
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) { throw 'uv kur: winget install --id=astral-sh.uv -e; ardından yeni terminal aç' }
if ($Backend -eq 'official') {
  $Vendor = Join-Path $Root 'vendor'
  New-Item -ItemType Directory -Force -Path $Vendor | Out-Null
  $Clone = Join-Path $Vendor 'blender_mcp'
  if (-not (Test-Path (Join-Path $Clone '.git'))) {
    & git clone 'https://projects.blender.org/lab/blender_mcp.git' $Clone
    if ($LASTEXITCODE -ne 0) { throw 'Klonlama başarısız' }
  } else { Write-Host 'Kaynak zaten mevcut, otomatik güncellenmedi.' }
  $ServerDir = Join-Path $Clone 'mcp'
  if (-not (Test-Path $ServerDir)) { throw "Sunucu dizini yok: $ServerDir" }
} else {
  & uvx mcp-for-blender install-addon
  if ($LASTEXITCODE -ne 0) { throw 'Topluluk addon kurulumu başarısız' }
}
if (Get-Command codex -ErrorAction SilentlyContinue) {
  $Existing = (& codex mcp list 2>$null | Out-String)
  if ($Existing -match '(?m)^\s*blender\s') {
    Write-Host 'Codex blender kaydı var, üzerine yazılmadı.'
    Write-Host 'Değiştirmek için önce: codex mcp remove blender'
  } elseif ($Backend -eq 'official') {
    & codex mcp add blender -- uv --directory $ServerDir run blender-mcp
    if ($LASTEXITCODE -ne 0) { throw 'Codex MCP ekleme başarısız' }
  } else {
    & codex mcp add blender -- uvx mcp-for-blender
    if ($LASTEXITCODE -ne 0) { throw 'Codex MCP ekleme başarısız' }
  }
  & codex mcp list
} else {
  Write-Host 'Codex yok; kurduktan sonra:'
  if ($Backend -eq 'official') {
    Write-Host ('codex mcp add blender -- uv --directory "{0}" run blender-mcp' -f $ServerDir)
  } else { Write-Host 'codex mcp add blender -- uvx mcp-for-blender' }
}
if ($Backend -eq 'official') {
  Write-Host 'Blender 5.1+ içinde resmî eklentiyi kur: https://www.blender.org/lab/mcp-server/'
} else { Write-Host 'Blender içinde N → MCP for Blender panelini kontrol et.' }
Write-Host 'İşlem tamam. MCP sunucusunu açmak için Blender çalışmalı.'
