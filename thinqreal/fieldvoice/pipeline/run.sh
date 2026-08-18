#!/usr/bin/env bash
# FieldVoice 웹 UI 실행 스크립트 — 처음이면 가상환경 생성 + 의존성 설치까지 자동
set -e
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3가 없습니다 — macOS는 xcode-select --install 또는 python.org에서 설치하세요."
  exit 1
fi

if [ ! -d venv ]; then
  echo "[1/3] 가상환경 생성 중..."
  python3 -m venv venv
fi

echo "[2/3] 의존성 확인 중..."
./venv/bin/pip install --quiet --upgrade pip
./venv/bin/pip install --quiet -r requirements.txt

# 분석 백엔드 확인 — Claude Code CLI(구독, 크레딧 불필요) 또는 Claude API 키
if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
  echo "ℹ 분석 백엔드: Claude API (ANTHROPIC_API_KEY)"
elif command -v claude >/dev/null 2>&1; then
  echo "ℹ 분석 백엔드: Claude Code CLI (구독 사용량 — API 크레딧 불필요)"
else
  echo ""
  echo "⚠ 분석 백엔드가 없습니다. 둘 중 하나를 준비하세요 (README §2):"
  echo "    Claude Code CLI 설치·로그인 (구독 활용 — 추가 비용 없음, 권장)"
  echo "    export ANTHROPIC_API_KEY=발급받은키 (API 크레딧 과금)"
  echo ""
fi

echo "[3/3] 웹 UI 시작 — 브라우저가 자동으로 열립니다."
exec ./venv/bin/python webapp.py
