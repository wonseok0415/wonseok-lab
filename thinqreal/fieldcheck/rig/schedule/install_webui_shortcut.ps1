# ============================================================
#  바탕화면에 'FieldCheck 조작판' 바로가기를 만든다 (Windows)
#
#  사용법 — PowerShell에서:
#    powershell -ExecutionPolicy Bypass -File schedule\install_webui_shortcut.ps1
#
#  더블클릭하면 조작판 서버가 켜지고 브라우저가 자동으로 열린다.
#  검은 서버 창을 닫으면 조작판이 꺼진다.
# ============================================================
$ErrorActionPreference = "Stop"

$RigDir = Split-Path -Parent $PSScriptRoot
$Target = Join-Path $RigDir "webui_start.bat"
if (-not (Test-Path $Target)) {
    Write-Host "[오류] webui_start.bat 를 찾을 수 없습니다: $Target" -ForegroundColor Red
    exit 1
}

$Desktop = [Environment]::GetFolderPath('Desktop')
$Shortcut = Join-Path $Desktop "FieldCheck 조작판.lnk"

$Wsh = New-Object -ComObject WScript.Shell
$sc = $Wsh.CreateShortcut($Shortcut)
$sc.TargetPath = $Target
$sc.WorkingDirectory = $RigDir
$sc.Description = "FieldCheck 점검 장비 조작판 (로컬 웹 UI)"
$sc.IconLocation = "$env:SystemRoot\System32\shell32.dll,177"
$sc.Save()

Write-Host "바탕화면에 바로가기를 만들었습니다: FieldCheck 조작판" -ForegroundColor Green
Write-Host "더블클릭하면 브라우저 조작판이 열립니다 (검은 창을 닫으면 종료)."
