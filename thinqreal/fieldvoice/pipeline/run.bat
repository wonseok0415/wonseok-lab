@echo off
rem FieldVoice 웹 UI 실행 (Windows) — 처음이면 가상환경 생성 + 의존성 설치까지 자동
chcp 65001 >nul
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo Python이 없습니다 — python.org에서 설치할 때 "Add python.exe to PATH"를 체크하세요.
  pause
  exit /b 1
)

if not exist venv (
  echo [1/3] 가상환경 생성 중...
  python -m venv venv
)

echo [2/3] 의존성 확인 중...
venv\Scripts\python -m pip install --quiet --upgrade pip
venv\Scripts\pip install --quiet -r requirements.txt

if defined ANTHROPIC_API_KEY (
  echo 분석 백엔드: Claude API ^(ANTHROPIC_API_KEY^)
) else (
  where claude >nul 2>nul
  if errorlevel 1 (
    echo.
    echo [주의] 분석 백엔드가 없습니다. 둘 중 하나를 준비하세요 - README 2절:
    echo    Claude Code CLI 설치·로그인 ^(구독 활용 - 추가 비용 없음, 권장^)
    echo    set ANTHROPIC_API_KEY=발급받은키 ^(API 크레딧 과금^)
    echo.
  ) else (
    echo 분석 백엔드: Claude Code CLI ^(구독 사용량 - API 크레딧 불필요^)
  )
)

echo [3/3] 웹 UI 시작 - 브라우저가 자동으로 열립니다. 종료: Ctrl+C
venv\Scripts\python webapp.py
pause
