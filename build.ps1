param(
    [switch]$SkipInstall,
    [switch]$SkipClean,
    [switch]$Sign,
    [string]$SignToolPath = "signtool.exe",
    [string]$TimestampUrl = "http://timestamp.digicert.com",
    [string]$OutputName = "YGOPRO_Blogger_Tool"
)

$ErrorActionPreference = "Stop"

function Step($Message) {
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Ensure-FileExists($PathValue, $ErrorMessage) {
    if (-not (Test-Path $PathValue)) {
        throw $ErrorMessage
    }
}

function Remove-DirectorySafely($PathValue, $DisplayName) {
    if (-not (Test-Path $PathValue)) {
        return
    }

    try {
        Remove-Item -LiteralPath $PathValue -Recurse -Force -ErrorAction Stop
    } catch {
        $message = $_.Exception.Message
        throw @"
Failed to clean ${DisplayName}: $PathValue

The most common cause is that a file in this folder is still open, usually:
- dist\YGOPRO_Blogger_Tool.exe is still running
- Explorer is previewing or locking the file

Please close the packaged app and any window using files under $DisplayName, then run build again.
If you want to keep the current output folder, run:
.\build.ps1 -SkipClean

Original error:
$message
"@
    }
}

function New-IconFromJpg($SourceJpg, $TargetIco) {
    Add-Type -AssemblyName System.Drawing

    $bitmap = [System.Drawing.Bitmap]::new($SourceJpg)
    try {
        $icon = [System.Drawing.Icon]::FromHandle($bitmap.GetHicon())
        try {
            $stream = [System.IO.File]::Open($TargetIco, [System.IO.FileMode]::Create)
            try {
                $icon.Save($stream)
            } finally {
                $stream.Dispose()
            }
        } finally {
            $icon.Dispose()
        }
    } finally {
        $bitmap.Dispose()
    }
}

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

$Python = Join-Path $ProjectRoot "venv\Scripts\python.exe"
$Requirements = Join-Path $ProjectRoot "requirements.txt"
$IconJpg = Join-Path $ProjectRoot "icon.jpg"
$IconIco = Join-Path $ProjectRoot "icon.ico"
$VersionFile = Join-Path $ProjectRoot "version_info.txt"
$DistDir = Join-Path $ProjectRoot "dist"
$BuildDir = Join-Path $ProjectRoot "build"
$ExePath = Join-Path $DistDir "$OutputName.exe"

Ensure-FileExists $Python "Missing virtualenv python: $Python"
Ensure-FileExists $Requirements "Missing requirements file: $Requirements"
Ensure-FileExists $IconJpg "Missing icon.jpg: $IconJpg"
Ensure-FileExists $VersionFile "Missing version_info.txt: $VersionFile"

if (-not $SkipInstall) {
    Step "Install or update dependencies"
    & $Python -m pip install --upgrade pip
    & $Python -m pip install -r $Requirements
}

Step "Run python compile check"
@'
import pathlib
import py_compile

for path in pathlib.Path(".").rglob("*.py"):
    if "venv" in path.parts:
        continue
    py_compile.compile(str(path), doraise=True)

print("python compile check ok")
'@ | & $Python -

if (-not $SkipClean) {
    Step "Clean build and dist"
    Remove-DirectorySafely -PathValue $BuildDir -DisplayName "build"
    Remove-DirectorySafely -PathValue $DistDir -DisplayName "dist"
}

Step "Generate icon.ico from icon.jpg"
New-IconFromJpg -SourceJpg $IconJpg -TargetIco $IconIco
Ensure-FileExists $IconIco "Failed to generate icon file: $IconIco"

Step "Prepare PyInstaller arguments"
$PyInstallerArgs = @(
    "-m", "PyInstaller",
    "--noconfirm",
    "--clean",
    "--windowed",
    "--onefile",
    "--name", $OutputName,
    "--icon", $IconIco,
    "--version-file", $VersionFile
)

$PyInstallerArgs += "main.py"

Step "Run PyInstaller"
& $Python @PyInstallerArgs

Ensure-FileExists $ExePath "Build failed. Output file not found: $ExePath"

Step "Build completed"
Write-Host "Output file: $ExePath" -ForegroundColor Green

if ($Sign) {
    Step "Run code signing"

    $ResolvedSignTool = $null
    if (Get-Command $SignToolPath -ErrorAction SilentlyContinue) {
        $ResolvedSignTool = $SignToolPath
    } elseif (Test-Path $SignToolPath) {
        $ResolvedSignTool = $SignToolPath
    }

    if (-not $ResolvedSignTool) {
        throw "signtool was not found. Use -SignToolPath with a full path."
    }

    & $ResolvedSignTool sign `
        /fd SHA256 `
        /td SHA256 `
        /tr $TimestampUrl `
        /a `
        $ExePath

    Step "Signing completed"
    Write-Host "Signed file: $ExePath" -ForegroundColor Green
} else {
    Step "Signing skipped"
    Write-Host "Use .\build.ps1 -Sign when you are ready to sign the exe." -ForegroundColor Yellow
}

Step "Recommended validation"
Write-Host "1. Launch dist\$OutputName.exe directly" -ForegroundColor White
Write-Host "2. Test on another Windows device without Python installed" -ForegroundColor White
Write-Host "3. Test card search, Word paste, and HTML export" -ForegroundColor White
