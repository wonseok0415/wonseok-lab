# ============================================================
#  매일 정해진 시각에 점검을 자동 실행 (Windows / 작업 스케줄러)
#  상주 리그(Windows 노트북)용
#
#  사용법 — PowerShell을 열고:
#    cd C:\fieldcheck\rig
#    powershell -ExecutionPolicy Bypass -File schedule\install_windows.ps1
#    powershell -ExecutionPolicy Bypass -File schedule\install_windows.ps1 -Time "08:15"
#
#  해제:
#    Unregister-ScheduledTask -TaskName "ThinQReal FieldCheck" -Confirm:$false
# ============================================================
param(
    [string]$Time = "07:00"
)

$ErrorActionPreference = "Stop"
$TaskName = "ThinQReal FieldCheck"

$RigDir = Split-Path -Parent $PSScriptRoot
$Python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $Python) {
    Write-Host "[오류] python을 찾을 수 없습니다. Python 설치 시 'Add python.exe to PATH'를 체크했는지 확인해 주세요." -ForegroundColor Red
    exit 1
}
if (-not (Test-Path (Join-Path $RigDir "config.json"))) {
    Write-Host "[오류] $RigDir\config.json 이 없습니다. config.example.json을 복사해 만들어 주세요." -ForegroundColor Red
    exit 1
}

$LogDir = Join-Path $RigDir "logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

# 로그를 남기기 위해 배치 파일로 감싼다 (작업 스케줄러는 출력 리디렉션을 직접 지원하지 않음)
$Runner = Join-Path $PSScriptRoot "run_once.bat"
@"
@echo off
cd /d "$RigDir"
rem 리디렉션된 출력은 cp949로 잡혀 한글 라벨의 특수문자에서 점검이 죽는다 - UTF-8 강제
set PYTHONIOENCODING=utf-8
echo ---------- %DATE% %TIME% ---------- >> "$LogDir\schedule.log"
"$Python" fieldcheck.py --once >> "$LogDir\schedule.log" 2>&1
"@ | Set-Content -Path $Runner -Encoding OEM

$action   = New-ScheduledTaskAction -Execute $Runner -WorkingDirectory $RigDir
$trigger  = New-ScheduledTaskTrigger -Daily -At $Time
# WakeToRun: 절전 중이면 깨워서 실행 / StartWhenAvailable: 그 시각을 놓쳤으면 이후에라도 실행
$settings = New-ScheduledTaskSettingsSet -WakeToRun -StartWhenAvailable `
            -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
            -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger `
    -Settings $settings -Description "ThinQ ON 자동 점검 (FieldCheck)" -Force | Out-Null

Write-Host "설치 완료 — 매일 $Time 에 점검이 자동 실행됩니다." -ForegroundColor Green
Write-Host "  작업 이름 : $TaskName  (작업 스케줄러에서 확인 가능)"
Write-Host "  실행 로그 : $LogDir\schedule.log"
Write-Host ""
Write-Host "지금 바로 한 번 실행해 확인:"
Write-Host "    Start-ScheduledTask -TaskName `"$TaskName`""
Write-Host "    Get-Content `"$LogDir\schedule.log`" -Tail 30 -Wait"
Write-Host ""
Write-Host "※ 스피커·마이크를 쓰므로 이 작업은 '사용자가 로그온한 경우에만' 실행됩니다." -ForegroundColor Yellow
Write-Host "   상주 리그는 로그온 상태로 두고 덮개만 닫아 두세요 (README 8번 설정 참고)."
