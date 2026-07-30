#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
#  ThinQ Real FieldCheck — 점검 리그 (구축 1단계: L1 무응답 감지)
#
#  동작: 저장된 점검 음성(WAV) 재생 → 마이크 녹음 → 응답 유무·지연시간 판정
#        → 결과를 Apps Script(health_checks)로 전송, 실패 시 담당자 메일
#
#  사용법 (자세한 안내는 README.md):
#    python fieldcheck.py --list-devices   스피커/마이크 장치 목록
#    python fieldcheck.py --calibrate      주변 소음 측정 → 임계값 추천
#    python fieldcheck.py --once           전체 시나리오 1회 점검
#    python fieldcheck.py --loop           주기 점검 (config의 loop_interval_minutes)
#    python fieldcheck.py --selftest       오디오 장치 없이 판정 로직 자체 검증
# ============================================================

import argparse
import datetime
import json
import math
import os
import sys
import time
import urllib.request

import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')
STATE_PATH = os.path.join(BASE_DIR, 'state.json')
LOG_PATH = os.path.join(BASE_DIR, 'results.jsonl')
REC_DIR = os.path.join(BASE_DIR, 'recordings')

FRAME_MS = 30  # 판정 프레임 길이 (ms)


# ── 설정/상태 파일 ──────────────────────────────────────────

def load_config():
    if not os.path.exists(CONFIG_PATH):
        sys.exit('[오류] config.json이 없습니다. config.example.json을 복사해 config.json을 만들고 값을 채워 주세요.')
    with open(CONFIG_PATH, encoding='utf-8') as f:
        return json.load(f)


def load_state():
    if os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH, encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {'consecutive_fails': {}}


def save_state(state):
    with open(STATE_PATH, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


# ── WAV 입출력 (표준 라이브러리 wave 사용, 16-bit PCM) ──────

def read_wav(path):
    import wave
    with wave.open(path, 'rb') as w:
        if w.getsampwidth() != 2:
            sys.exit(f'[오류] {path}: 16-bit PCM WAV만 지원합니다. synthesize_phrases.py로 다시 만들어 주세요.')
        sr = w.getframerate()
        data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
        if w.getnchannels() > 1:
            data = data.reshape(-1, w.getnchannels())[:, 0].copy()
    return data, sr


def write_wav(path, samples, samplerate):
    import wave
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(samplerate)
        w.writeframes(samples.astype(np.int16).tobytes())


# ── 판정 로직 (L1: 음성 활동 감지) ──────────────────────────

def frame_dbfs(seg):
    rms = math.sqrt(float(np.mean(seg.astype(np.float64) ** 2)))
    return 20 * math.log10(rms / 32768.0) if rms > 0 else -120.0


def analyze_recording(samples, samplerate, threshold_dbfs, min_voice_ms):
    """녹음에서 '지속적인 소리(=응답)'의 시작 시점을 찾는다.

    30ms 프레임 단위로 음량(dBFS)을 재고, 임계값 이상이
    min_voice_ms 이상 연속되면 응답으로 판정한다.
    """
    frame = max(1, int(samplerate * FRAME_MS / 1000))
    need = max(1, int(round(min_voice_ms / FRAME_MS)))
    run = 0
    candidate = 0
    start_sample = None
    peak = -120.0

    for i in range(0, len(samples) - frame + 1, frame):
        db = frame_dbfs(samples[i:i + frame])
        peak = max(peak, db)
        if db >= threshold_dbfs:
            if run == 0:
                candidate = i
            run += 1
            if run >= need and start_sample is None:
                start_sample = candidate
        else:
            run = 0

    if start_sample is None:
        return {'responded': False, 'latency_ms': None, 'peak_dbfs': round(peak, 1)}
    return {
        'responded': True,
        'latency_ms': int(start_sample / samplerate * 1000),
        'peak_dbfs': round(peak, 1),
    }


# ── 오디오 재생/녹음 (sounddevice는 필요할 때만 import) ────

def audio():
    try:
        import sounddevice as sd
        return sd
    except ImportError:
        sys.exit('[오류] sounddevice가 설치되지 않았습니다. 명령창에서:  pip install sounddevice numpy')


def run_scenario(cfg, scenario):
    sd = audio()
    sr = int(cfg.get('samplerate', 16000))
    out_dev = cfg.get('output_device')
    in_dev = cfg.get('input_device')
    gap = float(cfg.get('wake_gap_seconds', 0.8))
    listen = float(scenario.get('listen_seconds', 8))

    wake, wake_sr = read_wav(os.path.join(BASE_DIR, scenario['wake_file']))
    phrase, phrase_sr = read_wav(os.path.join(BASE_DIR, scenario['phrase_file']))

    print(f"  발화 재생 중... ({scenario['label']})")
    sd.play(wake, wake_sr, device=out_dev)
    sd.wait()
    time.sleep(gap)
    sd.play(phrase, phrase_sr, device=out_dev)
    sd.wait()

    print(f'  응답 대기/녹음 중... ({listen:.0f}초)')
    rec = sd.rec(int(listen * sr), samplerate=sr, channels=1, dtype='int16', device=in_dev)
    sd.wait()
    samples = rec[:, 0]

    now = datetime.datetime.now()
    rec_name = now.strftime('%Y%m%d_%H%M%S') + '_' + scenario['id'] + '.wav'
    rec_path = os.path.join(REC_DIR, rec_name)
    write_wav(rec_path, samples, sr)

    verdict = analyze_recording(
        samples, sr,
        float(cfg.get('voice_threshold_dbfs', -45)),
        int(cfg.get('min_voice_ms', 300)),
    )

    result = {
        'type': 'health_check',
        'apiKey': cfg.get('api_key', ''),
        'timestamp': now.isoformat(timespec='seconds'),
        'level': scenario.get('level', 'L1'),
        'scenario_id': scenario['id'],
        'scenario_label': scenario['label'],
        'result': 'pass' if verdict['responded'] else 'fail',
        'latency_ms': verdict['latency_ms'],
        'detail': json.dumps({'peak_dbfs': verdict['peak_dbfs'],
                              'threshold_dbfs': cfg.get('voice_threshold_dbfs', -45)},
                             ensure_ascii=False),
        'media_ref': rec_name,
        'note': '',
    }
    return result


# ── 결과 전송/기록 ──────────────────────────────────────────

def append_local_log(result):
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(result, ensure_ascii=False) + '\n')


def post_result(cfg, payload):
    url = cfg.get('endpoint_url', '')
    if not url or 'script.google.com' not in url:
        print('  [주의] endpoint_url이 설정되지 않아 서버 전송을 건너뜁니다 (로컬 기록만).')
        return False
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode('utf-8'))
        if body.get('success'):
            return True
        print(f"  [주의] 서버 응답 오류: {body}")
    except Exception as e:  # 네트워크 단절 등 — 점검 자체는 계속되어야 함
        print(f'  [주의] 서버 전송 실패: {e}')
    return False


def run_all(cfg):
    state = load_state()
    fails = state.setdefault('consecutive_fails', {})
    alert_after = int(cfg.get('consecutive_fails_for_alert', 1))
    summary = []

    for scenario in cfg.get('scenarios', []):
        print(f"[점검] {scenario['label']}")
        result = run_scenario(cfg, scenario)

        sid = scenario['id']
        if result['result'] == 'fail':
            fails[sid] = fails.get(sid, 0) + 1
        else:
            fails[sid] = 0
        # 연속 실패가 기준에 도달했을 때만 서버가 메일을 보내도록 표시
        result['alert'] = bool(result['result'] == 'fail' and fails[sid] >= alert_after)

        append_local_log(result)
        sent = post_result(cfg, result)

        mark = 'OK ' if result['result'] == 'pass' else 'FAIL'
        lat = f"{result['latency_ms']}ms" if result['latency_ms'] is not None else '-'
        print(f'  → [{mark}] 지연 {lat} / 서버 전송 {"성공" if sent else "안 됨(로컬 기록됨)"}'
              + (' / 담당자 메일 발송 요청' if result['alert'] else ''))
        summary.append(result)

    save_state(state)
    n_fail = sum(1 for r in summary if r['result'] == 'fail')
    print(f'\n[완료] {len(summary)}건 점검, 실패 {n_fail}건')
    return summary


def in_active_hours(cfg):
    rng = cfg.get('active_hours')
    if not rng:
        return True
    try:
        start_s, end_s = rng.split('-')
        now = datetime.datetime.now().time()
        start = datetime.time(*map(int, start_s.split(':')))
        end = datetime.time(*map(int, end_s.split(':')))
        return start <= now <= end
    except ValueError:
        print(f'[주의] active_hours 형식 오류({rng}) — "07:00-19:00" 형태여야 합니다. 항상 점검으로 동작.')
        return True


# ── 부가 명령 ───────────────────────────────────────────────

def cmd_list_devices():
    sd = audio()
    print(sd.query_devices())
    print('\n위 목록의 번호를 config.json의 output_device(스피커)/input_device(마이크)에 넣을 수 있습니다.')
    print('null로 두면 Windows 기본 장치를 사용합니다.')


def cmd_calibrate(cfg):
    sd = audio()
    sr = int(cfg.get('samplerate', 16000))
    print('주변 소음을 3초간 측정합니다. 조용히 해주세요...')
    rec = sd.rec(int(3 * sr), samplerate=sr, channels=1, dtype='int16', device=cfg.get('input_device'))
    sd.wait()
    ambient = frame_dbfs(rec[:, 0])
    suggest = min(-25.0, max(-55.0, ambient + 12))
    print(f'  주변 소음: {ambient:.1f} dBFS')
    print(f'  추천 임계값(voice_threshold_dbfs): {suggest:.0f}')
    print('  → config.json의 voice_threshold_dbfs를 위 값으로 설정한 뒤 --once로 테스트해 보세요.')


def cmd_selftest():
    """오디오 장치 없이 판정 로직만 검증한다 (합성 신호 사용)."""
    sr = 16000
    t = np.arange(sr * 2) / sr
    tone = (np.sin(2 * np.pi * 440 * t) * 32768 * 0.1).astype(np.int16)  # -20dBFS 근처 2초 톤
    silence = np.zeros(sr, dtype=np.int16)
    noise = (np.random.default_rng(0).normal(0, 30, sr * 3)).astype(np.int16)  # 아주 작은 잡음 3초

    ok = True

    v = analyze_recording(np.concatenate([silence, tone, silence]), sr, -45, 300)
    good = v['responded'] and abs(v['latency_ms'] - 1000) <= FRAME_MS * 2
    print(f'  [1] 1초 침묵 후 응답  → responded={v["responded"]}, latency={v["latency_ms"]}ms '
          + ('OK' if good else 'FAIL (기대: 약 1000ms)'))
    ok &= good

    v = analyze_recording(noise, sr, -45, 300)
    good = not v['responded']
    print(f'  [2] 무응답(잡음만)    → responded={v["responded"]} ' + ('OK' if good else 'FAIL'))
    ok &= good

    v = analyze_recording(np.concatenate([silence, tone[:int(sr * 0.1)], noise]), sr, -45, 300)
    good = not v['responded']
    print(f'  [3] 0.1초 순간 소음   → responded={v["responded"]} ' + ('OK (짧은 소음은 무시)' if good else 'FAIL'))
    ok &= good

    print('\n[selftest] ' + ('모두 통과' if ok else '실패 있음'))
    return 0 if ok else 1


# ── 메인 ────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description='ThinQ Real FieldCheck 점검 리그')
    p.add_argument('--once', action='store_true', help='전체 시나리오 1회 점검')
    p.add_argument('--loop', action='store_true', help='주기 점검 (Ctrl+C로 중지)')
    p.add_argument('--calibrate', action='store_true', help='주변 소음 측정 및 임계값 추천')
    p.add_argument('--list-devices', action='store_true', help='오디오 장치 목록')
    p.add_argument('--selftest', action='store_true', help='판정 로직 자체 검증 (장치 불필요)')
    args = p.parse_args()

    if args.selftest:
        sys.exit(cmd_selftest())
    if args.list_devices:
        cmd_list_devices()
        return

    cfg = load_config()

    if args.calibrate:
        cmd_calibrate(cfg)
        return
    if args.once:
        run_all(cfg)
        return
    if args.loop:
        interval = float(cfg.get('loop_interval_minutes', 30))
        print(f'[loop] {interval:.0f}분 간격 주기 점검을 시작합니다. 중지: Ctrl+C')
        while True:
            if in_active_hours(cfg):
                run_all(cfg)
            else:
                print(f'[loop] 점검 시간대(active_hours={cfg.get("active_hours")}) 밖 — 이번 회차 건너뜀')
            time.sleep(interval * 60)

    p.print_help()


if __name__ == '__main__':
    main()
