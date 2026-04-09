param(
    [string]$Root = "C:\AI_WORKSPACE\M33-Lotto-Bot-VN",
    [string]$OutFile = "i18n_scan_report.txt"
)

$ErrorActionPreference = "Stop"

$Targets = @(
    "src\app\main.py",
    "src\modules\bet",
    "src\modules\result",
    "src\modules\admin",
    "src\bot\menus",
    "src\bot\handlers",
    "src\modules\report"
)

$KeywordPatterns = @(
    "Bet Accepted",
    "Invalid",
    "Please",
    "Date:",
    "Today",
    "Region",
    "Number",
    "Mode",
    "Total",
    "Winning Details",
    "Settlement Report",
    "Transactions Report",
    "Number Detail",
    "Version",
    "Telegram",
    "Back",
    "Cancel",
    "Confirm",
    "Refresh",
    "Admin",
    "Info"
)

$ApiPatterns = @(
    "reply_text\(",
    "edit_message_text\(",
    "query\.answer\(",
    "InlineKeyboardButton",
    "KeyboardButton",
    "ReplyKeyboardMarkup",
    "InlineKeyboardMarkup"
)

function Get-LineType {
    param([string]$Line)

    $s = $Line.ToLower()

    if ($s -match "inlinekeyboardbutton|keyboardbutton|replykeyboardmarkup|inlinekeyboardmarkup") { return "button" }
    if ($s -match "reply_text\(|edit_message_text\(|query\.answer\(") { return "prompt" }

    if ($s -match "bet accepted|success|done|completed|updated|saved|refreshed") { return "success" }
    if ($s -match "invalid|error|unauthorized|denied|not found|incomplete|fail|failed") { return "error" }
    if ($s -match "please|enter|choose|select|return|back|confirm|cancel|refresh|now in|date:|today") { return "prompt" }
    if ($s -match "region|number|mode|total|winning details|settlement report|transactions report|number detail") { return "formatter" }
    if ($s -match "version|telegram|about|info|help|guide|further information") { return "info" }

    return "menu"
}

function Get-TextSample {
    param([string]$Line)
    $t = $Line.Trim()
    if ($t.Length -gt 180) { return $t.Substring(0,180) + "..." }
    return $t
}

function Scan-File {
    param([string]$FilePath)

    $results = @()
    $lines = Get-Content -LiteralPath $FilePath -ErrorAction SilentlyContinue
    if ($null -eq $lines) { return $results }

    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        $lineNo = $i + 1

        $matched = $false
        $hitKind = $null

        foreach ($p in $ApiPatterns) {
            if ($line -match $p) {
                $matched = $true
                $hitKind = "api"
                break
            }
        }

        if (-not $matched) {
            foreach ($k in $KeywordPatterns) {
                if ($line -like "*$k*") {
                    $matched = $true
                    $hitKind = "keyword"
                    break
                }
            }
        }

        if ($matched) {
            $type = Get-LineType -Line $line
            $results += [PSCustomObject]@{
                Path = $FilePath
                LineNumber = $lineNo
                Type = $type
                Kind = $hitKind
                Sample = Get-TextSample -Line $line
            }
        }
    }

    return $results
}

$allResults = @()

foreach ($target in $Targets) {
    $full = Join-Path $Root $target
    if (-not (Test-Path $full)) { continue }

    if ((Get-Item $full).PSIsContainer) {
        $files = Get-ChildItem -LiteralPath $full -Recurse -File -Filter *.py
    } else {
        $files = @((Get-Item -LiteralPath $full))
    }

    foreach ($f in $files) {
        $allResults += Scan-File -FilePath $f.FullName
    }
}

$allResults = $allResults | Sort-Object Path, LineNumber

$report = New-Object System.Text.StringBuilder
[void]$report.AppendLine("I18N SCAN REPORT")
[void]$report.AppendLine(("Root: {0}" -f $Root))
[void]$report.AppendLine(("Generated: {0}" -f (Get-Date)))
[void]$report.AppendLine("")

$currentPath = $null
foreach ($row in $allResults) {
    if ($row.Path -ne $currentPath) {
        $currentPath = $row.Path
        [void]$report.AppendLine(("FILE: {0}" -f $currentPath))
    }

    [void]$report.AppendLine(("  [{0}] line {1}: {2}" -f $row.Type, $row.LineNumber, $row.Sample))
}
if ($allResults.Count -eq 0) {
    [void]$report.AppendLine("No matches found.")
}

$reportText = $report.ToString()
$reportText | Out-File -LiteralPath (Join-Path $Root $OutFile) -Encoding UTF8

Write-Host $reportText
Write-Host ""
Write-Host ("Saved to: {0}" -f (Join-Path $Root $OutFile))