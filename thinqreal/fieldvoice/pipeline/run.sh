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

# Claude API 인증 확인 (ANTHROPIC_API_KEY 또는 ant 프로필 — 없어도 UI는 뜨지만 분석 단계에서 실패)
if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
  if ! command -v ant >/dev/null 2>&1 || ! ant auth status >/dev/null 2>&1; then
    echo ""
    echo "⚠ Claude API 인증이 아직 없습니다. 둘 중 하나를 준비하세요 (README §2):"
    echo "    export ANTHROPIC_API_KEY=발급받은키"
    echo "    ant auth login"
    echo ""
  fi
fi

echo "[3/3] 웹 UI 시작 — 브라우저가 자동으로 열립니다."
exec ./venv/bin/python webapp.py
