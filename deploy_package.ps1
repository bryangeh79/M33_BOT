$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$stageDir = Join-Path $projectRoot ".deploy-stage-$timestamp"
$zipPath = Join-Path $projectRoot "m33-lotto-bot-vn-$timestamp.zip"

$excludeNames = @(
    '.git',
    '.deploy-stage-*',
    '__pycache__',
    '.pytest_cache',
    '.venv',
    'venv',
    'node_modules',
    'data',
    'configs',
    '.env',
    '*.db',
    '*.log',
    '*.zip'
)

Write-Host "Creating stage dir: $stageDir"
New-Item -ItemType Directory -Path $stageDir | Out-Null

Get-ChildItem -Force -Path $projectRoot | Where-Object {
    $name = $_.Name
    -not ($excludeNames | Where-Object { $name -like $_ })
} | ForEach-Object {
    Copy-Item $_.FullName -Destination $stageDir -Recurse -Force
}

if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}

Write-Host "Creating zip: $zipPath"
Compress-Archive -Path (Join-Path $stageDir '*') -DestinationPath $zipPath -Force

Write-Host "Done: $zipPath"
Write-Host "Remember: configs/, data/, .env are intentionally excluded."

Remove-Item $stageDir -Recurse -Force
