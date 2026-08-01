#!/bin/bash
# ============================================================
#  매일 정해진 시각에 점검을 자동 실행 (macOS / launchd)
#
#  사용법:
#    bash schedule/install_macos.sh          → 매일 07:30 실행
#    bash schedule/install_macos.sh 8 15     → 매일 08:15 실행
#
#  해제:
#    bash schedule/uninstall_macos.sh
# ============================================================
set -euo pipefail

HOUR="${1:-7}"
MIN="${2:-30}"
LABEL="com.thinqreal.fieldcheck"

RIG_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
LOG_DIR="$RIG_DIR/logs"

PY="$(command -v python3 || true)"
if [ -z "$PY" ]; then
  echo "[오류] python3을 찾을 수 없습니다. 터미널에서 python3 --version 이 되는지 확인해 주세요."
  exit 1
fi
if [ ! -f "$RIG_DIR/config.json" ]; then
  echo "[오류] $RIG_DIR/config.json 이 없습니다."
  echo "       config.example.json을 복사해 config.json을 먼저 만들어 주세요."
  exit 1
fi

mkdir -p "$HOME/Library/LaunchAgents" "$LOG_DIR"

cat > "$PLIST" <<PLIST_EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>$PY</string>
    <string>$RIG_DIR/fieldcheck.py</string>
    <string>--once</string>
  </array>
  <key>WorkingDirectory</key>
  <string>$RIG_DIR</string>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key><integer>$HOUR</integer>
    <key>Minute</key><integer>$MIN</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>$LOG_DIR/schedule.log</string>
  <key>StandardErrorPath</key>
  <string>$LOG_DIR/schedule.log</string>
  <key>RunAtLoad</key>
  <false/>
</dict>
</plist>
PLIST_EOF

launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"

printf '설치 완료 — 매일 %02d:%02d 에 점검이 자동 실행됩니다.\n' "$HOUR" "$MIN"
echo "  등록 파일 : $PLIST"
echo "  실행 로그 : $LOG_DIR/schedule.log"
echo
echo "▶ 지금 바로 한 번 실행해서 확인 (마이크 권한 창이 뜨면 '허용'):"
echo "    launchctl kickstart -p gui/$(id -u)/$LABEL"
echo "    tail -f \"$LOG_DIR/schedule.log\""
echo
echo "▶ 그 시각에 맥이 잠들어 있으면 실행되지 않습니다. 자동으로 깨우려면 (관리자 암호 필요):"
printf '    sudo pmset repeat wakeorpoweron MTWRFSU %02d:%02d:00\n' "$HOUR" "$((MIN > 5 ? MIN - 5 : 0))"
echo "    (평일만 원하면 MTWRFSU 대신 MTWRF)"
