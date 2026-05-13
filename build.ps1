$ErrorActionPreference = "Stop"

$python = ".\venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "找不到 $python"
}

& $python -m PyInstaller `
  --noconfirm `
  --clean `
  --windowed `
  --onefile `
  --name YGOPRO_Blogger_Tool `
  --add-data "HTML_template;HTML_template" `
  main.py
