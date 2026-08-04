#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
#  ThinQ Real FieldCheck — L3 카메라 측정 도구 (구축 3단계 사전 검증)
#
#  목적: 가전 제어(조명 등)의 물리적 변화를 카메라 픽셀 비교로 판정할 수
#        있는지 실측하는 독립 도구. AI 영상 인식을 쓰지 않는다 (DESIGN.md §5).
#        기존 점검(fieldcheck.py)과 완전히 분리되어 있어 자동 점검에 영향 없음.
#
#  개념: 대상 영역(조명 기구가 보이는 사각형)과 참조 영역(조명과 무관하게
#        변하지 않는 벽 한 조각)의 평균 밝기를 함께 측정한다. 카메라가 자동
#        노출로 화면 전체 밝기를 바꿔도, '대상 ÷ 참조' 상대값은 조명의 실제
#        변화만 남긴다.
#
#  사용법 (첫 실험: 사람이 조명을 손으로 껐다 켜며 지표 변화를 관찰):
#    python3 vision.py --pick             대상/참조 영역을 마우스로 지정 (1회)
#    python3 vision.py --watch 60         60초간 1초 간격 측정 (Ctrl+C로 중단)
#    python3 vision.py --snapshot         1장 촬영해 저장 (구도 확인용)
#    옵션: --device N  카메라 번호 (기본 0 = 내장 카메라)
#          --interval 초  측정 간격 (기본 1.0)
#
#  준비: pip3 install opencv-python
#  ⚠ 마이크와 같은 macOS 권한 함정이 카메라에도 있다 — 터미널에서 첫 실행 시
#    '카메라 접근' 허용 창이 뜨면 반드시 [허용]. 거부되면 오류 없이 검은
#    화면만 들어오므로, 이 도구는 검은 프레임을 감지하면 경고를 출력한다.
# ============================================================

import argparse
import csv
import datetime
import json
import os
import sys
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROI_PATH = os.path.join(BASE_DIR, 'camera_roi.json')
LOG_DIR = os.path.join(BASE_DIR, 'logs')
CSV_PATH = os.path.join(LOG_DIR, 'camera_test.csv')
SNAP_DIR = os.path.join(BASE_DIR, 'recordings', 'camera')

try:
    import cv2
    import numpy as np
except ImportError:
    sys.exit('[오류] opencv-python이 필요합니다. 터미널에서 설치해 주세요:\n'
             '    pip3 install opencv-python')


# ── 카메라 열기 ─────────────────────────────────────────────

def open_camera(device):
    cap = cv2.VideoCapture(device)
    if not cap.isOpened():
        sys.exit(f'[오류] 카메라 {device}번을 열 수 없습니다.\n'
                 '  ① 다른 앱(FaceTime 등)이 카메라를 쓰고 있지 않은지 확인\n'
                 '  ② 시스템 설정 → 개인정보 보호 및 보안 → 카메라 → 터미널 허용 여부 확인')
    # 자동 노출이 안정될 때까지 몇 프레임 버린다 (첫 프레임은 어둡게 나오는 경우가 많음)
    for _ in range(10):
        cap.read()
        time.sleep(0.05)
    return cap


def grab_gray(cap):
    ok, frame = cap.read()
    if not ok or frame is None:
        return None, None
    return frame, cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


def is_black(gray):
    # 권한 거부 시 macOS는 오류 없이 검은 프레임을 반환한다 (마이크 무음 함정과 동일 구조)
    return gray is not None and float(gray.mean()) < 2.0


BLACK_HINT = ('[주의] 카메라에서 검은 화면만 들어옵니다 — 카메라 권한 문제일 가능성이 큽니다.\n'
              '       시스템 설정 → 개인정보 보호 및 보안 → 카메라 → 터미널을 허용한 뒤 다시 실행해 주세요.')


# ── 관심영역(ROI) 지정/저장 ─────────────────────────────────

def load_roi():
    if not os.path.exists(ROI_PATH):
        return None
    with open(ROI_PATH, encoding='utf-8') as f:
        return json.load(f)


def roi_mean(gray, rect):
    x, y, w, h = rect
    part = gray[y:y + h, x:x + w]
    return float(part.mean()) if part.size else 0.0


def pick_rois(device):
    cap = open_camera(device)
    frame, gray = grab_gray(cap)
    cap.release()
    if frame is None:
        sys.exit('[오류] 프레임을 읽지 못했습니다.')
    if is_black(gray):
        sys.exit(BLACK_HINT)

    print('카메라 화면 창이 열립니다. 마우스로 사각형을 그린 뒤 Enter(또는 Space)로 확정하세요.')
    print('  1번째: 대상 영역 — 조명 기구(또는 빛이 크게 변하는 곳)가 보이는 사각형')
    target = cv2.selectROI('1) TARGET: light area  (drag + Enter)', frame, showCrosshair=False)
    print('  2번째: 참조 영역 — 조명과 무관하게 변하지 않는 벽/가구 한 조각')
    ref = cv2.selectROI('2) REFERENCE: unchanging wall  (drag + Enter)', frame, showCrosshair=False)
    cv2.destroyAllWindows()

    if target[2] == 0 or target[3] == 0 or ref[2] == 0 or ref[3] == 0:
        sys.exit('[오류] 영역이 지정되지 않았습니다. 드래그로 사각형을 그린 뒤 Enter를 눌러 주세요.')

    data = {'device': device, 'target': [int(v) for v in target], 'reference': [int(v) for v in ref]}
    with open(ROI_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'저장 완료 → {ROI_PATH}')
    print(f'  대상 {data["target"]} / 참조 {data["reference"]}')
    print('※ 맥북(카메라)을 옮기거나 덮개 각도를 바꾸면 --pick으로 다시 지정해야 합니다.')


# ── 구도 확인용 1장 촬영 ────────────────────────────────────

def snapshot(device):
    cap = open_camera(device)
    frame, gray = grab_gray(cap)
    cap.release()
    if frame is None:
        sys.exit('[오류] 프레임을 읽지 못했습니다.')
    if is_black(gray):
        print(BLACK_HINT)
    os.makedirs(SNAP_DIR, exist_ok=True)
    path = os.path.join(SNAP_DIR, datetime.datetime.now().strftime('snap_%Y%m%d_%H%M%S.jpg'))
    cv2.imwrite(path, frame)
    print(f'저장 완료 → {path}')
    print('사진을 열어 조명과 참조용 벽이 화면에 잘 들어왔는지 확인하세요.')


# ── 실시간 측정 (첫 실험용) ─────────────────────────────────

def watch(device, seconds, interval):
    roi = load_roi()
    if roi is None:
        sys.exit('[안내] 먼저 영역을 지정해 주세요:  python3 vision.py --pick')

    cap = open_camera(device)
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(SNAP_DIR, exist_ok=True)
    new_csv = not os.path.exists(CSV_PATH)
    rows = []

    print(f'{seconds}초간 {interval}초 간격으로 측정합니다. 측정 중에 조명을 손으로 껐다 켜 주세요. (Ctrl+C로 중단)')
    print()
    print('  시각        대상 밝기   참조 밝기   상대값(대상/참조)')
    print('  ' + '-' * 52)

    with open(CSV_PATH, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if new_csv:
            writer.writerow(['timestamp', 'target_mean', 'reference_mean', 'ratio'])
        start = time.time()
        first_saved = False
        try:
            while time.time() - start < seconds:
                frame, gray = grab_gray(cap)
                if gray is None:
                    print('  [주의] 프레임 읽기 실패 — 건너뜀')
                    time.sleep(interval)
                    continue
                if is_black(gray):
                    print(BLACK_HINT)
                    break
                t = roi_mean(gray, roi['target'])
                r = roi_mean(gray, roi['reference'])
                ratio = t / r if r > 0.5 else 0.0
                now = datetime.datetime.now()
                print(f'  {now.strftime("%H:%M:%S")}   {t:8.1f}   {r:8.1f}   {ratio:8.3f}')
                writer.writerow([now.isoformat(timespec="seconds"), f'{t:.1f}', f'{r:.1f}', f'{ratio:.3f}'])
                rows.append((t, r, ratio))
                if not first_saved:
                    cv2.imwrite(os.path.join(SNAP_DIR, now.strftime('watch_start_%Y%m%d_%H%M%S.jpg')), frame)
                    first_saved = True
                time.sleep(interval)
        except KeyboardInterrupt:
            print('\n  (중단됨 — 여기까지의 측정으로 요약합니다)')
        finally:
            cap.release()

    if len(rows) < 3:
        sys.exit('[안내] 측정 데이터가 너무 적습니다. 다시 실행해 주세요.')

    targets = [x[0] for x in rows]
    ratios = [x[2] for x in rows]
    refs = [x[1] for x in rows]
    print()
    print('── 요약 ─────────────────────────────────────────')
    print(f'  대상 밝기   최소 {min(targets):6.1f} / 최대 {max(targets):6.1f} / 변화폭 {max(targets) - min(targets):6.1f}')
    print(f'  참조 밝기   최소 {min(refs):6.1f} / 최대 {max(refs):6.1f} / 변화폭 {max(refs) - min(refs):6.1f}')
    print(f'  상대값      최소 {min(ratios):6.3f} / 최대 {max(ratios):6.3f}')
    spread = max(ratios) - min(ratios)
    mid = (max(ratios) + min(ratios)) / 2
    if spread > 0.15:
        print(f'  → 상대값 변화폭 {spread:.3f} — 조명 ON/OFF 구분이 뚜렷합니다.')
        print(f'    판정 임계값 후보: 상대값 {mid:.3f} (이보다 크면 켜짐, 작으면 꺼짐)')
    else:
        print(f'  → 상대값 변화폭 {spread:.3f} — 구분이 약합니다. 대상 영역을 조명 기구에 더 가깝게')
        print('    다시 지정(--pick)하거나, 카메라 각도를 조정해 보세요.')
    print(f'  기록: {CSV_PATH}')


# ── 진입점 ──────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description='FieldCheck L3 카메라 측정 도구 (독립 실행)')
    p.add_argument('--pick', action='store_true', help='대상/참조 영역을 마우스로 지정')
    p.add_argument('--watch', nargs='?', const=60, type=int, metavar='초', help='실시간 측정 (기본 60초)')
    p.add_argument('--snapshot', action='store_true', help='1장 촬영해 저장 (구도 확인)')
    p.add_argument('--device', type=int, default=0, help='카메라 번호 (기본 0 = 내장)')
    p.add_argument('--interval', type=float, default=1.0, help='측정 간격 초 (기본 1.0)')
    args = p.parse_args()

    if args.pick:
        pick_rois(args.device)
    elif args.watch is not None:
        watch(args.device, args.watch, args.interval)
    elif args.snapshot:
        snapshot(args.device)
    else:
        p.print_help()


if __name__ == '__main__':
    main()
