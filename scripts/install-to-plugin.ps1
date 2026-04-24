# install-to-plugin.ps1
# Copies the project-log skill into your Cowork plugin skills folder so it shows up in Claude's
# skill list across all projects.
#
# Usage (from the repo root):
#   pwsh ./scripts/install-to-plugin.ps1
# or
#   powershell -ExecutionPolicy Bypass -File .\scripts\install-to-plugin.ps1

$ErrorActionPreference = "Stop"

$repoRoot  = Split-Path -Parent $PSScriptRoot
$source    = Join-Path $repoRoot ".claude\skills\project-log"
$pluginDir = Join-Path $env:APPDATA "Claude\local-agent-mode-sessions\skills-plugin"

if (-not (Test-Path $source)) {
    Write-Error "Skill source not found at $source"
    exit 1
}

if (-not (Test-Path $pluginDir)) {
    Write-Error "Cowork plugin folder not found at $pluginDir. Is Cowork installed?"
    exit 1
}

# Find the deepest 'skills' folder inside the plugin tree — Cowork nests it under session/plugin GUIDs.
$skillsDirs = Get-ChildItem -Path $pluginDir -Recurse -Filter "skills" -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notlike "*node_modules*" }

if (-not $skillsDirs) {
    Write-Error "No 'skills' folder found under $pluginDir. Open Cowork once first so it creates the structure."
    exit 1
}

# Prefer the most-recently-modified one (matches the active session/plugin)
$target = ($skillsDirs | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
$destination = Join-Path $target "project-log"

Write-Host "Source:      $source"
Write-Host "Destination: $destination"
Write-Host ""

if (Test-Path $destination) {
    $response = Read-Host "Destination exists. Overwrite? (y/N)"
    if ($response -ne "y") {
        Write-Host "Aborted."
        exit 0
    }
    Remove-Item -Recurse -Force $destination
}

Copy-Item -Recurse -Path $source -Destination $destination
Write-Host ""
Write-Host "Installed. Restart Cowork to pick up the new skill."
