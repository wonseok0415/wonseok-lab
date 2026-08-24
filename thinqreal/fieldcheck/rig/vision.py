#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
#  ThinQ Real FieldCheck — L3 카메라 측정/판정 모듈
#
#  역할 두 가지:
#    ① 독립 도구 — 사전 검증용 수동 측정 (--snapshot / --pick / --watch)
#    ② fieldcheck.py의 L3 판정 모듈 — 가전 제어 전후의 픽셀 변화 판정
#
#  판정 원리 (DESIGN.md §5 — AI 영상 인식 불사용):
#    대상 영역(조명 기구)과 참조 영역(변하지 않는 벽)의 평균 밝기 '상대값
#    (대상÷참조)'을 본다. 카메라 자동 노출이 화면 전체 밝기를 바꿔도 상대값은
#    조명의 실제 변화만 남긴다 — 2026-08-04 현장 실측으로 검증
#    (꺼짐 0.746 ↔ 켜짐 1.063, 참조 영역 절대 밝기는 49나 출렁였음).
#
#  독립 도구 사용법 (첫 실험: 조명을 손으로 껐다 켜며 관찰):
#    python3 vision.py --pick             대상/참조 영역을 마우스로 지정 (1회)
#    python3 vision.py --watch 60         60초간 1초 간격 측정 (Ctrl+C로 중단)
#    python3 vision.py --snapshot         1장 촬영해 저장 (구도 확인용)
#
#  준비: pip3 install opencv-python
#  ⚠ 마이크와 같은 macOS 권한 함정이 카메라에도 있다 — 허용 창이 뜬 그 실행은
#    실패하고 다음 실행부터 성공. 거부하면 오류 없이 검은 화면만 들어오므로
#    검은 프레임을 감지하면 경고한다.
#  ⚠ opencv 미설치여도 이 모듈의 import는 실패하지 않는다 (fieldcheck.py가
#    L1/L2 전용 장비에서도 돌아야 하므로). 카메라 기능만 조용히 비활성화된다.
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
    cv2 = None

INSTALL_HINT = ('[오류] opencv-python이 필요합니다. 터미널에서 설치해 주세요:\n'
                '    python3 -m pip install --user opencv-python')

BLACK_HINT = ('[주의] 카메라에서 검은 화면만 들어옵니다 — 카메라 권한 문제일 가능성이 큽니다.\n'
              '       시스템 설정 → 개인정보 보호 및 보안 → 카메라 → 터미널을 허용한 뒤 다시 실행해 주세요.')


def available():
    return cv2 is not None


# ── 카메라 열기/촬영 ────────────────────────────────────────

def _open_camera(device):
    cap = cv2.VideoCapture(device)
    if not cap.isOpened():
        return None
    # 자동 노출이 안정될 때까지 몇 프레임 버린다 (첫 프레임은 어둡게 나오는 경우가 많음)
    for _ in range(10):
        cap.read()
        time.sleep(0.05)
    return cap


def _grab_gray(cap):
    ok, frame = cap.read()
    if not ok or frame is None:
        return None, None
    return frame, cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


def _is_black(gray):
    # 권한 거부 시 macOS는 오류 없이 검은 프레임을 반환한다 (마이크 무음 함정과 동일 구조)
    return gray is not None and float(gray.mean()) < 2.0


def _roi_mean(gray, rect):
    x, y, w, h = rect
    part = gray[y:y + h, x:x + w]
    return float(part.mean()) if part.size else 0.0


def _ratio(gray, roi):
    t = _roi_mean(gray, roi['target'])
    r = _roi_mean(gray, roi['reference'])
    return t, r, (t / r if r > 0.5 else 0.0)


def load_roi():
    if not os.path.exists(ROI_PATH):
        return None
    with open(ROI_PATH, encoding='utf-8') as f:
        return json.load(f)


# ── fieldcheck.py용 API ─────────────────────────────────────

def capture_ratio_once(device, roi, frames=3, interval=0.3):
    """현재 상태의 상대값 1점 측정 (L3 사전 상태 확인용).

    반환: (ok, ratio, problem, bright)
      bright = (대상 절대 밝기, 참조 절대 밝기) — 상대값만으로는 "제3의 광원이
      켜져 있어 방이 이미 밝다"를 구분할 수 없어 함께 남긴다
      (2026-08-24 현장: 조명 다 껐는데 상대값 1.036 — 절대 밝기가 있어야 판독 가능).
      ok=False면 problem에 원인 문자열 — '점검 장비 문제'로 분류해야 함.
    """
    cap = _open_camera(device)
    if cap is None:
        return False, None, '카메라를 열 수 없음 (연결/다른 앱 점유/권한)', None
    samples = []
    try:
        for _ in range(frames):
            _, gray = _grab_gray(cap)
            if gray is None:
                continue
            if _is_black(gray):
                return False, None, '검은 화면만 수신 (카메라 권한/렌즈 가림)', None
            samples.append(_ratio(gray, roi))
            time.sleep(interval)
    finally:
        cap.release()
    if not samples:
        return False, None, '프레임을 읽지 못함', None
    samples.sort(key=lambda s: s[2])
    mid = samples[len(samples) // 2]
    return True, round(mid[2], 3), '', (round(mid[0], 1), round(mid[1], 1))


def capture_series(device, roi, seconds, interval=1.0, prefix='l3'):
    """가전 동작 구간의 연속 측정 (발화 후 seconds초, interval초 간격).

    반환: {'ok', 'problem', 'series': [(경과초, 대상, 참조, 상대값), ...], 'snapshot'}
    snapshot은 마지막 프레임 저장 파일명 (실패 원인 확인용).
    """
    cap = _open_camera(device)
    if cap is None:
        return {'ok': False, 'problem': '카메라를 열 수 없음 (연결/다른 앱 점유/권한)',
                'series': [], 'snapshot': ''}
    os.makedirs(SNAP_DIR, exist_ok=True)
    series = []
    last_frame = None
    start = time.time()
    try:
        while time.time() - start < seconds:
            frame, gray = _grab_gray(cap)
            if gray is None:
                time.sleep(interval)
                continue
            if _is_black(gray):
                return {'ok': False, 'problem': '검은 화면만 수신 (카메라 권한/렌즈 가림)',
                        'series': series, 'snapshot': ''}
            t, r, ratio = _ratio(gray, roi)
            series.append((round(time.time() - start, 1), round(t, 1), round(r, 1), round(ratio, 3)))
            last_frame = frame
            time.sleep(interval)
    finally:
        cap.release()
    if not series:
        return {'ok': False, 'problem': '프레임을 읽지 못함', 'series': [], 'snapshot': ''}
    snap = ''
    if last_frame is not None:
        snap = datetime.datetime.now().strftime(f'{prefix}_%Y%m%d_%H%M%S.jpg')
        cv2.imwrite(os.path.join(SNAP_DIR, snap), last_frame)
    return {'ok': True, 'problem': '', 'series': series, 'snapshot': snap}


def judge_light(before_ratio, series, min_delta=0.15, expect='on', sustain=3):
    """조명 판정 — '변화량(Δ)' 기준, 순수 계산 (opencv 불필요, selftest 가능).

    before_ratio: 발화 전 상대값. series: capture_series의 series.
    expect: 'on'(밝아짐 기대) / 'off'(어두워짐 기대).
    sustain: 변위가 이 표본 수만큼 연속 지속되어야 변화로 인정 (스파이크 배제).

    절대 임계값이 아니라 **명령 직후의 변화량**을 본다 (2026-08-05 현장 발견):
    상대값의 절대 수준은 시각·채광(커튼 상태)에 따라 통째로 떠다니지만
    — 오전 꺼짐 0.746/켜짐 1.063, 낮 꺼짐 0.911/켜짐 1.225 —
    ON↔OFF의 변화폭은 ~0.31로 안정적이었다. 채광은 천천히 변하고 루틴의
    효과는 명령 직후 급변하므로, Δ 기준은 시각·날씨와 무관하게 성립한다.

    판정 원칙: 사전 상태가 이미 목표 상태면 변화가 없어 실패(판정 불가)로
    남는다 — 켜기(복합 명령)→외출(꺼짐+복구) 쌍 구성으로 시작 상태를 보장할 것.
    """
    # 판정 기준의 진화 (전부 현장 실측이 근거):
    # ① 크기만 본다 (2026-08-05): 태양 각도에 따라 같은 가전 동작이 상대값을
    #    올리기도 내리기도 한다 — 외출 루틴(어두워짐) 정상 동작에 Δ+0.433.
    #    방향은 진단 참고값(direction_match)으로만 기록한다.
    # ② 최종 상태가 아니라 촬영 구간 전체의 '최대 지속 변위'를 본다 (2026-08-07):
    #    복합 명령(다운라이트 켜기+커튼 열기)은 두 효과가 상대값에 반대 방향으로
    #    작용한다 — 조명은 대상을 밝히고(↑), 커튼 채광은 참조 벽을 밝힌다(↓).
    #    실제로 둘 다 동작했는데 순변화가 Δ-0.1에 그쳐 실패로 오판된 사례.
    #    구간 중 어느 시점이든 |Δ|≥min_delta가 sustain표본 연속이면 물리 변화다.
    want_on = (expect != 'off')

    ratios = [s[3] for s in series]
    if not ratios or before_ratio is None:
        return {'passed': False, 'reason': '측정 데이터 없음', 'action_latency_ms': None,
                'before_ratio': before_ratio, 'after_ratio': None,
                'peak_delta': None, 'direction_match': None}
    tail = ratios[-sustain:]
    after = round(sum(tail) / len(tail), 3)
    final_delta = round(after - before_ratio, 3)

    peak_delta = 0.0
    run = 0
    hit_idx = None
    for i, r in enumerate(ratios):
        d = r - before_ratio
        if abs(d) > abs(peak_delta):
            peak_delta = d
        if abs(d) >= min_delta:
            run += 1
            if run >= sustain and hit_idx is None:
                hit_idx = i - run + 1
        else:
            run = 0
    peak_delta = round(peak_delta, 3)

    if hit_idx is not None:
        direction_match = (peak_delta > 0) == want_on
        notes = []
        if not direction_match:
            notes.append('※ 변화 방향이 기대와 반대 — 태양 각도에 따라 방향은 뒤집힐 수 있어 참고만')
        if abs(final_delta) < min_delta:
            notes.append('※ 종료 시점엔 변화가 상쇄됨 — 조명·커튼 동시 동작의 상반 효과(정상)')
        # 첫 표본부터 이미 기준을 넘겼다면 변화는 촬영 시작 전(발화·확답 구간)에
        # 끝난 것 — 0ms로 기록하면 반응 시간 통계가 오염되므로 미측정으로 남긴다
        if hit_idx == 0:
            latency = None
            notes.append('※ 촬영 시작 시점에 이미 변화 완료 — 반응이 확답·촬영 준비 구간보다 빨라 반응 시간 미측정')
        else:
            latency = int(series[hit_idx][0] * 1000)
        note = (' ' + ' '.join(notes)) if notes else ''
        return {'passed': True,
                'reason': f'물리 변화 감지 — 상대값 {before_ratio} 기준 최대 변위 Δ{peak_delta:+} '
                          f'(기준 |Δ|≥{min_delta} {sustain}표본 지속, 종료 시 {after}){note}',
                'action_latency_ms': latency,
                'before_ratio': before_ratio, 'after_ratio': after,
                'peak_delta': peak_delta, 'direction_match': direction_match}

    return {'passed': False,
            'reason': f'물리 변화 미감지 — 상대값 {before_ratio}→{after} '
                      f'(최대 변위 Δ{peak_delta:+}, 기준 |Δ|≥{min_delta} {sustain}표본 지속). '
                      '명령 미동작 또는 점검 전 이미 목표 상태',
            'action_latency_ms': None, 'before_ratio': before_ratio, 'after_ratio': after,
            'peak_delta': peak_delta, 'direction_match': None}


# ── 독립 도구 (수동 측정) ───────────────────────────────────

def pick_rois(device):
    cap = _open_camera(device)
    if cap is None:
        sys.exit('[오류] 카메라를 열 수 없습니다.\n'
                 '  ① 다른 앱(FaceTime 등)이 카메라를 쓰고 있지 않은지 확인\n'
                 '  ② 시스템 설정 → 개인정보 보호 및 보안 → 카메라 → 터미널 허용 여부 확인')
    frame, gray = _grab_gray(cap)
    cap.release()
    if frame is None:
        sys.exit('[오류] 프레임을 읽지 못했습니다.')
    if _is_black(gray):
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


def snapshot(device):
    cap = _open_camera(device)
    if cap is None:
        sys.exit('[오류] 카메라를 열 수 없습니다 (연결/다른 앱 점유/권한 확인).')
    frame, gray = _grab_gray(cap)
    cap.release()
    if frame is None:
        sys.exit('[오류] 프레임을 읽지 못했습니다.')
    if _is_black(gray):
        print(BLACK_HINT)
    os.makedirs(SNAP_DIR, exist_ok=True)
    path = os.path.join(SNAP_DIR, datetime.datetime.now().strftime('snap_%Y%m%d_%H%M%S.jpg'))
    cv2.imwrite(path, frame)
    print(f'저장 완료 → {path}')
    print('사진을 열어 조명과 참조용 벽이 화면에 잘 들어왔는지 확인하세요.')


def watch(device, seconds, interval):
    roi = load_roi()
    if roi is None:
        sys.exit('[안내] 먼저 영역을 지정해 주세요:  python3 vision.py --pick')

    cap = _open_camera(device)
    if cap is None:
        sys.exit('[오류] 카메라를 열 수 없습니다 (연결/다른 앱 점유/권한 확인).')
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
                frame, gray = _grab_gray(cap)
                if gray is None:
                    print('  [주의] 프레임 읽기 실패 — 건너뜀')
                    time.sleep(interval)
                    continue
                if _is_black(gray):
                    print(BLACK_HINT)
                    break
                t, r, ratio = _ratio(gray, roi)
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
    refs = [x[1] for x in rows]
    ratios = [x[2] for x in rows]
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

    if not available():
        sys.exit(INSTALL_HINT)

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
