#!/bin/bash
# 자동 실행 해제 (macOS)
set -euo pipefail

LABEL="com.thinqreal.fieldcheck"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"

launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
rm -f "$PLIST"

echo "자동 실행을 해제했습니다. ($PLIST 삭제)"
echo
echo "맥 자동 기상 설정도 함께 껐다면 아래로 해제할 수 있습니다 (관리자 암호 필요):"
echo "    sudo pmset repeat cancel"
