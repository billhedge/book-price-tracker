#Requires -Version 7
<#
.SYNOPSIS
    Download a web page as an HTML test fixture, with a source comment at the top.

.DESCRIPTION
    Prompts for anything not given on the command line. Saves the page to
    tests\fixtures\<name>.html (relative to the repo root, wherever you run it from),
    then adds a comment recording the URL and the capture date. The file is
    UTF-8 without a byte order mark. Assumes the page itself is UTF-8.

.EXAMPLE
    .\scripts\capture-fixture.ps1

.EXAMPLE
    .\scripts\capture-fixture.ps1 -Url "https://books.toscrape.com/catalogue/category/books/horror_31/index.html" -Name category_horror_page1
#>
[CmdletBinding()]
param(
    [string]$Url,
    [string]$Name,
    [switch]$Force    # overwrite an existing fixture without asking
)

$ErrorActionPreference = 'Stop'

if (-not $Url)  { $Url  = Read-Host 'Page URL' }
if (-not $Name) { $Name = Read-Host 'Fixture name (letters, digits, _ and -, no extension)' }

$Url  = $Url.Trim()
# Lowercased because CI runs on Linux, where file names are case-sensitive.
$Name = $Name.Trim().ToLowerInvariant() -replace '\.html$', ''

if ($Url -notmatch '^https?://') {
    throw "Not an http or https URL: $Url"
}
if ($Name -notmatch '^[a-z0-9_-]+$') {
    throw "Use letters, digits, underscores, and hyphens only: $Name"
}

$fixtures = Join-Path $PSScriptRoot '..' 'tests' 'fixtures'
New-Item -ItemType Directory -Force -Path $fixtures | Out-Null
$file = Join-Path $fixtures "$Name.html"
$part = "$file.part"

if ((Test-Path -LiteralPath $file) -and -not $Force) {
    $answer = Read-Host "$Name.html already exists and tests may depend on it. Overwrite? (y/N)"
    if ($answer -notmatch '^[yY]') {
        Write-Host 'Nothing changed.'
        exit 0
    }
}

try {
    # curl writes the bytes itself (-o), so PowerShell never decodes them.
    # -f: fail on an HTTP error instead of saving the error page. -S: still show the error.
    # Download to a .part file so a failure never damages an existing fixture.
    curl.exe -sSf $Url -o $part
    if ($LASTEXITCODE -ne 0) {
        throw "curl failed with exit code $LASTEXITCODE"
    }

    $date   = Get-Date -Format yyyy-MM-dd
    $header = "<!-- Source: $Url`n     Captured: $date with curl.exe. Unmodified apart from this comment. -->`n"
    $body   = Get-Content -LiteralPath $part -Raw -Encoding utf8
    Set-Content -LiteralPath $file -Value ($header + $body) -NoNewline -Encoding utf8NoBOM
}
finally {
    if (Test-Path -LiteralPath $part) { Remove-Item -LiteralPath $part }
}

Write-Host "Saved tests\fixtures\$Name.html"
