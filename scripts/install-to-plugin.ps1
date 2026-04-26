# install-to-plugin.ps1
# Copies the project-log skill + its 7 slash-command siblings into your Cowork plugin skills folder
# so /where, /roadmap, /idea, /bootstrap, /replan, /ship, /log register as real slash commands.
# Preserves personal memory entries on reinstall (only scaffold files are overwritten).
#
# Usage (from the repo root):
#   pwsh ./scripts/install-to-plugin.ps1
# or
#   powershell -ExecutionPolicy Bypass -File .\scripts\install-to-plugin.ps1

$ErrorActionPreference = "Stop"

$repoRoot  = Split-Path -Parent $PSScriptRoot
$skillsSrc = Join-Path $repoRoot ".claude\skills"
$pluginDir = Join-Path $env:APPDATA "Claude\local-agent-mode-sessions\skills-plugin"

# The 8 skills this repo ships
$skillNames = @("project-log", "where", "roadmap", "idea", "bootstrap", "replan", "ship", "log")

if (-not (Test-Path $skillsSrc)) { Write-Error "Skills source not found at $skillsSrc"; exit 1 }
if (-not (Test-Path $pluginDir)) { Write-Error "Cowork plugin folder not found at $pluginDir. Is Cowork installed?"; exit 1 }

# Find the deepest 'skills' folder inside the plugin tree — Cowork nests it under session/plugin GUIDs.
$skillsDirs = Get-ChildItem -Path $pluginDir -Recurse -Filter "skills" -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notlike "*node_modules*" }

if (-not $skillsDirs) { Write-Error "No 'skills' folder found under $pluginDir. Open Cowork once first."; exit 1 }

# Prefer the most-recently-modified one (matches the active session/plugin)
$target = ($skillsDirs | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName

Write-Host "Source:   $skillsSrc"
Write-Host "Target:   $target"
Write-Host "Skills:   $($skillNames -join ', ')"
Write-Host ""

# Check for any existing installs
$existing = $skillNames | Where-Object { Test-Path (Join-Path $target $_) }
if ($existing) {
    Write-Host "These skills already exist in the target: $($existing -join ', ')"
    $response = Read-Host "Overwrite all? (y/N)"
    if ($response -ne "y") { Write-Host "Aborted."; exit 0 }
}

foreach ($name in $skillNames) {
    $src = Join-Path $skillsSrc $name
    $dst = Join-Path $target $name
    if (-not (Test-Path $src)) { Write-Warning "Skipping $name — source not found at $src"; continue }
    # Merge-copy (do NOT Remove-Item $dst): -Force overwrites same-named files,
    # leaves everything else (e.g. user's personal memory/<type>_*.md entries) untouched.
    if (-not (Test-Path $dst)) { New-Item -ItemType Directory -Force -Path $dst | Out-Null }
    Copy-Item -Recurse -Force -Path (Join-Path $src "*") -Destination $dst
    Write-Host "  [+] $name"
}

Write-Host ""
Write-Host "Installed. FULLY quit Cowork (tray icon -> Quit) and reopen so the skills are rescanned."
