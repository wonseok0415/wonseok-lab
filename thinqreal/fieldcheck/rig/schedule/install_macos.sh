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
#
#  ── 왜 python3을 직접 실행하지 않는가 (2026-08-01 현장 확인) ──
#  launchd가 python3을 직접 실행하면 macOS가 마이크 권한 요청 창을 띄우지
#  않는다. 앱 번들이 아닌 실행 파일은 TCC(개인정보 보호) 대상으로 인정되지
#  않아, 권한을 묻지도 않고 조용히 '무음'을 돌려준다. 시스템 설정의 마이크
#  목록에도 나타나지 않아 수동으로 켤 수도 없다.
#  → 정식 앱 번들인 터미널을 통해 실행한다. 터미널은 권한 창이 정상적으로
#    뜨고, 한 번 허용하면 이후 계속 유지된다.
# ============================================================
set -euo pipefail

HOUR="${1:-7}"
MIN="${2:-30}"
LABEL="com.thinqreal.fieldcheck"

RIG_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
LOG_DIR="$RIG_DIR/logs"
RUNNER="$RIG_DIR/schedule/run_once.command"

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

# 터미널이 열어서 실행할 스크립트 (.command 확장자여야 터미널이 실행함)
cat > "$RUNNER" <<RUNNER_EOF
#!/bin/bash
# 자동 생성 파일 — schedule/install_macos.sh가 만듭니다. 직접 수정하지 마세요.
cd "$RIG_DIR"
echo "---------- \$(date '+%Y-%m-%d %H:%M:%S') ----------" >> "$LOG_DIR/schedule.log"
"$PY" fieldcheck.py --once 2>&1 | tee -a "$LOG_DIR/schedule.log"
RUNNER_EOF
chmod +x "$RUNNER"

cat > "$PLIST" <<PLIST_EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/open</string>
    <string>-a</string>
    <string>Terminal</string>
    <string>$RUNNER</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key><integer>$HOUR</integer>
    <key>Minute</key><integer>$MIN</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>$LOG_DIR/launchd.log</string>
  <key>StandardErrorPath</key>
  <string>$LOG_DIR/launchd.log</string>
  <key>RunAtLoad</key>
  <false/>
</dict>
</plist>
PLIST_EOF

launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"

printf '설치 완료 — 매일 %02d:%02d 에 점검이 자동 실행됩니다.\n' "$HOUR" "$MIN"
echo "  등록 파일 : $PLIST"
echo "  실행 파일 : $RUNNER  (터미널 창이 열리며 실행됩니다)"
echo "  실행 로그 : $LOG_DIR/schedule.log"
echo
echo "▶ 지금 한 번 실행해서 마이크 권한을 승인하세요 (ThinQ ON 근처, 시연 중이 아닐 때):"
echo "    launchctl kickstart -p gui/$(id -u)/$LABEL"
echo "    → 새 터미널 창이 열립니다."
echo "    → '터미널이(가) 마이크에 접근하려고 합니다' 창이 뜨면 반드시 [허용]"
echo "      (이 승인은 한 번만 하면 이후 계속 유지됩니다)"
echo
echo "▶ 그 시각에 맥이 잠들어 있으면 실행되지 않습니다. 자동으로 깨우려면 (관리자 암호 필요):"
printf '    sudo pmset repeat wakeorpoweron MTWRFSU %02d:%02d:00\n' "$HOUR" "$((MIN > 5 ? MIN - 5 : 0))"
echo "    (평일만 원하면 MTWRFSU 대신 MTWRF)"
