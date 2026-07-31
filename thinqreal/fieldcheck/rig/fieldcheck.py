#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
#  ThinQ Real FieldCheck — 점검 리그
#    구축 1단계: L1 무응답 감지
#    구축 2단계: 예약 슬롯 자동 회피 + L2 내용 판정(로컬 STT)
#
#  동작: (예약 확인) → 저장된 점검 음성(WAV) 재생 → 마이크 녹음
#        → L1 응답 유무·지연시간 판정 → L2 내용 판정(STT + 키워드)
#        → 결과를 Apps Script(health_checks)로 전송, 아침 요약 메일로 보고
#
#  사용법 (자세한 안내는 README.md):
#    python fieldcheck.py --list-devices   스피커/마이크 장치 목록
#    python fieldcheck.py --calibrate      주변 소음 측정 → 임계값 추천
#    python fieldcheck.py --once           전체 시나리오 1회 점검
#    python fieldcheck.py --loop           주기 점검 (config의 loop_interval_minutes)
#    python fieldcheck.py --selftest       오디오 장치 없이 판정 로직 자체 검증
#    python fieldcheck.py --transcribe A.wav [시나리오ID]   녹음 파일 L2 판정만 시험
#    (--once/--loop에 --force를 붙이면 예약 시간대에도 강제로 점검)
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

import booking
import stt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')
STATE_PATH = os.path.join(BASE_DIR, 'state.json')
LOG_PATH = os.path.join(BASE_DIR, 'results.jsonl')
REC_DIR = os.path.join(BASE_DIR, 'recordings')

FRAME_MS = 30       # 판정 프레임 길이 (ms)
BAND_LOW_HZ = 250   # 음성 대역 하한 — 에어컨/선풍기 저주파 소음 배제
BAND_HIGH_HZ = 4000 # 음성 대역 상한


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


_WEIGHT_CACHE = {}


def _a_weight_linear(freqs):
    """IEC 61672 A-가중 곡선 — 사람 귀의 주파수별 민감도 반영 (선형 배율)."""
    f2 = np.maximum(freqs, 1e-6) ** 2
    ra = (12194.0 ** 2 * f2 ** 2) / (
        (f2 + 20.6 ** 2)
        * np.sqrt((f2 + 107.7 ** 2) * (f2 + 737.9 ** 2))
        * (f2 + 12194.0 ** 2)
    )
    a_db = 20 * np.log10(ra) + 2.0
    return 10 ** (a_db / 10)          # 파워 스케일 배율


def frame_dba(seg, samplerate, cal_offset=0.0):
    """프레임의 A-가중 음성 대역(250~4000Hz) 레벨을 dBA로 측정.

    - A-가중: 사람 귀 기준 감도로 주파수별 가중 (dBA 표기의 근거)
    - 대역 제한: 팬/에어컨 저주파 소음 배제 (A-가중과 이중 방어)
    - cal_offset: 휴대폰 소음측정 앱 등 실측과 한 번 비교해 넣는 보정값.
      0이면 상대 dBA (판정에는 상대값으로 충분 — 바닥 대비 차이만 사용)
    """
    key = (len(seg), samplerate)
    if key not in _WEIGHT_CACHE:
        freqs = np.fft.rfftfreq(len(seg), 1.0 / samplerate)
        band = (freqs >= BAND_LOW_HZ) & (freqs <= BAND_HIGH_HZ)
        _WEIGHT_CACHE[key] = (band, _a_weight_linear(freqs), np.hanning(len(seg)))
    band, weight, window = _WEIGHT_CACHE[key]

    x = seg.astype(np.float64) / 32768.0
    power = np.abs(np.fft.rfft(x * window)) ** 2
    e = float(np.mean((power * weight)[band])) if band.any() else 0.0
    return (10 * math.log10(e) if e > 0 else -120.0) + cal_offset


def analyze_recording(samples, samplerate, over_floor_db=8.0,
                      window_s=1.0, voiced_ratio=0.7, cal_offset=0.0):
    """녹음에서 '음성 응답'의 시작 시점을 찾는다. (적응형 판정, dBA 기준)

    1) 30ms 프레임마다 A-가중 음성 대역(250~4000Hz) 레벨(dBA)을 잰다
       — 에어컨/선풍기 저주파 소음은 대역 제한 + A-가중으로 이중 배제.
    2) 프레임 값들의 하위 10퍼센타일을 '소음 바닥'으로 삼는다
       — 환경마다 다른 소음 수준에 자동 적응 (절대 임계값 불필요).
    3) 바닥보다 over_floor_db(기본 8dB) 이상 솟은 프레임을 발성으로 보고,
       1초 구간(window_s) 안에서 발성 비율이 voiced_ratio(70%) 이상이면
       음성 응답으로 판정한다.

    비율 방식을 쓰는 이유: ThinQ ON의 연산 대기음('띵띵띵…', 짧은 효과음 +
    간격의 반복)은 발성 비율이 낮아 걸러지고, 사람 말(연속 발성)만 잡힌다.
    TTS 장애로 '듣고 연산음은 내지만 말을 못 하는' 상태를 FAIL로 잡는 것이
    L1의 핵심이므로, 효과음을 응답으로 인정하면 안 된다.

    cal_offset(dba_calibration_offset)이 0이면 상대 dBA — 판정은 바닥 대비
    차이만 쓰므로 보정 없이도 정확하다. 실측 소음계와 숫자를 맞추고 싶을
    때만 보정하면 된다 (README 'dBA 보정' 참조).
    """
    frame = max(1, int(samplerate * FRAME_MS / 1000))
    dbs = []
    for i in range(0, len(samples) - frame + 1, frame):
        dbs.append(frame_dba(samples[i:i + frame], samplerate, cal_offset))
    if not dbs:
        return {'responded': False, 'latency_ms': None, 'floor_dba': None, 'peak_dba': None}

    # 하위 10퍼센타일 = 소음 바닥. 완전 무음(-120) 구간이 바닥을 비현실적으로
    # 끌어내리지 않도록 하한을 둔다 (실제 마이크 환경엔 완전 무음이 없음).
    floor = max(float(np.percentile(dbs, 10)), -85.0 + cal_offset)
    thr = floor + over_floor_db
    peak = max(dbs)
    voiced = [d >= thr for d in dbs]

    win = max(1, int(round(window_s * 1000 / FRAME_MS)))
    for s in range(0, len(voiced) - win + 1):
        seg = voiced[s:s + win]
        if sum(seg) / win >= voiced_ratio:
            first = s + seg.index(True)
            return {
                'responded': True,
                'latency_ms': int(first * FRAME_MS),
                'floor_dba': round(floor, 1),
                'peak_dba': round(peak, 1),
            }
    return {'responded': False, 'latency_ms': None,
            'floor_dba': round(floor, 1), 'peak_dba': round(peak, 1)}


# ── 오디오 재생/녹음 (sounddevice는 필요할 때만 import) ────

def audio():
    try:
        import sounddevice as sd
        return sd
    except ImportError:
        sys.exit('[오류] sounddevice가 설치되지 않았습니다. 명령창에서:  pip install sounddevice numpy')


def wait_for_quiet(cfg, sd):
    """앞 시나리오의 응답(생성형 AI라 길이가 크게 변동)이 끝날 때까지 대기.

    마이크를 0.5초 단위로 살피다가 post_silence_seconds(기본 2초) 동안
    조용하면 응답이 끝난 것으로 보고 반환한다. 무한 대기를 막기 위해
    max_response_wait_seconds(기본 60초)에서 강제 종료한다.
    """
    sr = int(cfg.get('samplerate', 16000))
    thr = float(cfg.get('voice_threshold_dbfs', -45))
    quiet_needed = float(cfg.get('post_silence_seconds', 2.0))
    max_wait = float(cfg.get('max_response_wait_seconds', 60))
    chunk = 0.5
    waited = 0.0
    quiet = 0.0
    while waited < max_wait and quiet < quiet_needed:
        rec = sd.rec(int(chunk * sr), samplerate=sr, channels=1, dtype='int16',
                     device=cfg.get('input_device'))
        sd.wait()
        if frame_dbfs(rec[:, 0]) < thr:
            quiet += chunk
        else:
            quiet = 0.0
        waited += chunk
    if waited >= max_wait:
        print(f'  [주의] {max_wait:.0f}초가 지나도 소리가 이어져 대기를 종료합니다 (다음 점검에 영향 가능).')
    return waited


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

    cal = float(cfg.get('dba_calibration_offset', 0.0))
    verdict = analyze_recording(
        samples, sr,
        float(cfg.get('voice_over_floor_db', 8.0)),
        float(cfg.get('speech_window_seconds', 1.0)),
        float(cfg.get('speech_voiced_ratio', 0.7)),
        cal,
    )
    rel = '' if cal else ' (상대값 — 실측 보정은 README §dBA 보정)'
    print(f'  판정 참고: 소음 바닥 {verdict["floor_dba"]}dBA / 최고 {verdict["peak_dba"]}dBA '
          f'(음성 인정 기준: 바닥+{cfg.get("voice_over_floor_db", 8.0)}dB){rel}')

    # 생성형 답변은 녹음 창보다 길 수 있고, 무응답 '판정'이라도 실제 답변이
    # 창이 끝난 뒤 늦게 시작될 수 있다 (현장 관측: 영화 질문 — 긴 연산 후 답변,
    # 그 답변이 다음 시나리오의 기동어를 씹음). 판정 결과와 무관하게
    # 조용해질 때까지 기다린 뒤 다음 시나리오로 넘어간다.
    print('  주변이 조용해질 때까지 대기...')
    wait_for_quiet(cfg, sd)

    base = {
        'type': 'health_check',
        'apiKey': cfg.get('api_key', ''),
        'timestamp': now.isoformat(timespec='seconds'),
        'scenario_id': scenario['id'],
        'scenario_label': scenario['label'],
        'media_ref': rec_name,
        'note': '',
    }
    l1 = dict(base, **{
        'level': 'L1',
        'result': 'pass' if verdict['responded'] else 'fail',
        'latency_ms': verdict['latency_ms'],
        'detail': json.dumps({'floor_dba': verdict['floor_dba'],
                              'peak_dba': verdict['peak_dba'],
                              'cal_offset': cal,
                              'over_floor_db': cfg.get('voice_over_floor_db', 8.0),
                              'voiced_ratio': cfg.get('speech_voiced_ratio', 0.7)},
                             ensure_ascii=False),
        'stt_text': '',
        'expected': '',
    })
    results = [l1]

    # L2(내용 판정)는 L1이 통과했을 때만 — 응답 자체가 없으면 판정할 말이 없고,
    # 같은 실패를 두 건으로 세면 통계가 왜곡된다. 따라서 L2 성공률은
    # "응답한 것 중 내용까지 맞은 비율"로 읽어야 한다.
    if verdict['responded'] and stt.available(cfg):
        l2 = judge_content(cfg, scenario, samples, sr, base)
        if l2:
            results.append(l2)
    return results


def judge_content(cfg, scenario, samples, samplerate, base):
    """녹음을 텍스트로 바꿔 내용을 판정한다. STT 엔진이 없으면 None."""
    print('  응답 내용 인식 중(STT)...')
    started = time.time()
    text = stt.transcribe(samples, samplerate, cfg)
    if text is None:
        return None
    took = int((time.time() - started) * 1000)
    verdict = stt.judge(text, scenario, cfg)
    print(f'  인식 결과: "{text[:80]}{"…" if len(text) > 80 else ""}"')
    print(f'  내용 판정: {"통과" if verdict["passed"] else "실패"} — {verdict["reason"]}')
    return dict(base, **{
        'level': 'L2',
        'result': 'pass' if verdict['passed'] else 'fail',
        'latency_ms': None,
        'detail': json.dumps({'engine': stt._ENGINE, 'stt_ms': took,
                              'reason': verdict['reason']}, ensure_ascii=False),
        'stt_text': text,
        'expected': verdict['expected'],
    })


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


def run_all(cfg, force=False):
    state = load_state()

    allowed, reason = booking.check(cfg, state)
    if not allowed and not force:
        print(f'[건너뜀] {reason}')
        save_state(state)
        return []
    if not allowed:
        print(f'[주의] {reason} → --force 지정으로 강행합니다.')
    else:
        print(f'[예약 확인] {reason}')

    fails = state.setdefault('consecutive_fails', {})
    alert_after = int(cfg.get('consecutive_fails_for_alert', 1))
    summary = []

    for scenario in cfg.get('scenarios', []):
        print(f"[점검] {scenario['label']}")

        for result in run_scenario(cfg, scenario):
            key = result['level'] + ':' + scenario['id']
            if result['result'] == 'fail':
                fails[key] = fails.get(key, 0) + 1
            else:
                fails[key] = 0
            # 연속 실패가 기준에 도달했을 때만 서버가 메일을 보내도록 표시
            result['alert'] = bool(result['result'] == 'fail' and fails[key] >= alert_after)

            append_local_log(result)
            sent = post_result(cfg, result)

            mark = 'OK ' if result['result'] == 'pass' else 'FAIL'
            lat = f"{result['latency_ms']}ms" if result['latency_ms'] is not None else '-'
            print(f'  → [{result["level"]} {mark}] 지연 {lat} / 서버 전송 '
                  f'{"성공" if sent else "안 됨(로컬 기록됨)"}'
                  + (' / 담당자 메일 발송 요청' if result['alert'] else ''))
            summary.append(result)

    save_state(state)
    n_fail = sum(1 for r in summary if r['result'] == 'fail')
    print(f'\n[완료] {len(summary)}건 판정, 실패 {n_fail}건')
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
    cal = float(cfg.get('dba_calibration_offset', 0.0))
    print('주변 소음을 3초간 측정합니다. 조용히 해주세요...')
    rec = sd.rec(int(3 * sr), samplerate=sr, channels=1, dtype='int16', device=cfg.get('input_device'))
    sd.wait()
    samples = rec[:, 0]

    frame = max(1, int(sr * FRAME_MS / 1000))
    dbas = [frame_dba(samples[i:i + frame], sr, cal)
            for i in range(0, len(samples) - frame + 1, frame)]
    ambient_dba = float(np.mean(dbas))
    ambient = frame_dbfs(samples)
    suggest = min(-25.0, max(-55.0, ambient + 12))

    print(f'  주변 소음: {ambient_dba:.1f} dBA' + ('' if cal else ' (상대값)'))
    if not cal:
        print('  → 실제 소음계 숫자와 맞추려면: 휴대폰 소음측정 앱으로 같은 자리에서 측정 후')
        print('    config.json의 dba_calibration_offset = (앱 측정값) - (위 표시값) 으로 설정')
    print(f'  응답 종료 대기용 임계값(voice_threshold_dbfs) 추천: {suggest:.0f}')
    print('  → config.json에 반영한 뒤 --once로 테스트해 보세요. (응답 판정 자체는 자동 적응이라 별도 설정 불필요)')


def cmd_transcribe(cfg, wav_path, scenario_id=None):
    """이미 저장된 녹음으로 L2(내용 판정)만 시험한다 — 발화 없이 키워드 튜닝용."""
    path = wav_path if os.path.isabs(wav_path) else os.path.join(BASE_DIR, wav_path)
    if not os.path.exists(path):
        alt = os.path.join(REC_DIR, wav_path)
        if os.path.exists(alt):
            path = alt
        else:
            sys.exit(f'[오류] 파일을 찾을 수 없습니다: {wav_path}')

    samples, sr = read_wav(path)
    scenarios = cfg.get('scenarios', [])
    if scenario_id:
        match = [s for s in scenarios if s['id'] == scenario_id]
        if not match:
            sys.exit(f'[오류] config.json에 시나리오 "{scenario_id}"가 없습니다. '
                     f'있는 것: {", ".join(s["id"] for s in scenarios)}')
        scenario = match[0]
    else:
        # 파일명이 "..._시나리오ID.wav" 형식이면 자동으로 찾는다
        stem = os.path.splitext(os.path.basename(path))[0]
        match = [s for s in scenarios if stem.endswith(s['id'])]
        scenario = match[0] if match else {'id': '(미지정)', 'label': '(미지정)'}

    print(f'파일 : {os.path.basename(path)}')
    print(f'시나리오: {scenario.get("label", scenario["id"])}')
    text = stt.transcribe(samples, sr, cfg)
    if text is None:
        sys.exit('[오류] 위 사유로 내용 판정을 진행할 수 없습니다.')
    verdict = stt.judge(text, scenario, cfg)
    print(f'인식 결과: "{text}"')
    print(f'기대 조건: {verdict["expected"] or "(없음)"}')
    print(f'판정     : {"통과" if verdict["passed"] else "실패"} — {verdict["reason"]}')


def cmd_selftest():
    """오디오 장치 없이 판정 로직만 검증한다 (합성 신호 사용)."""
    sr = 16000
    t = np.arange(sr * 2) / sr
    tone = (np.sin(2 * np.pi * 440 * t) * 32768 * 0.1).astype(np.int16)  # 음성 대역 2초 톤
    silence = np.zeros(sr, dtype=np.int16)
    noise = (np.random.default_rng(0).normal(0, 30, sr * 3)).astype(np.int16)  # 아주 작은 잡음 3초

    # 선풍기/에어컨 흉내 — 저주파(70·110·170Hz) 정상 소음, 꽤 큰 소리 (5초)
    tf = np.arange(sr * 5) / sr
    fan = ((np.sin(2 * np.pi * 70 * tf) + np.sin(2 * np.pi * 110 * tf)
            + np.sin(2 * np.pi * 170 * tf)) * 32768 * 0.08).astype(np.int16)

    beep = tone[:int(sr * 0.25)]                     # 0.25초 '띵'
    gap = np.zeros(int(sr * 0.75), dtype=np.int16)   # 0.75초 간격
    chime = np.concatenate([beep, gap] * 5)          # 연산 대기음 흉내 (5초)

    talk_on = tone[:int(sr * 0.8)]                   # 0.8초 발성
    talk_off = np.zeros(int(sr * 0.15), dtype=np.int16)  # 0.15초 어절 사이 쉼
    speech = np.concatenate([talk_on, talk_off] * 4)     # 말소리 흉내

    ok = True

    v = analyze_recording(np.concatenate([silence, tone, silence]), sr)
    good = v['responded'] and abs(v['latency_ms'] - 1000) <= FRAME_MS * 3
    print(f'  [1] 1초 침묵 후 응답        → responded={v["responded"]}, latency={v["latency_ms"]}ms '
          + ('OK' if good else 'FAIL (기대: 약 1000ms)'))
    ok &= good

    v = analyze_recording(noise, sr)
    good = not v['responded']
    print(f'  [2] 무응답(잡음만)          → responded={v["responded"]} ' + ('OK' if good else 'FAIL'))
    ok &= good

    v = analyze_recording(np.concatenate([noise[:sr], tone[:int(sr * 0.1)], noise]), sr)
    good = not v['responded']
    print(f'  [3] 잡음 속 0.1초 순간 소음 → responded={v["responded"]} ' + ('OK (짧은 소음은 무시)' if good else 'FAIL'))
    ok &= good

    v = analyze_recording(np.concatenate([silence, chime]), sr)
    good = not v['responded']
    print(f'  [4] 연산 대기음(띵띵띵)     → responded={v["responded"]} ' + ('OK (효과음은 응답 아님)' if good else 'FAIL'))
    ok &= good

    v = analyze_recording(np.concatenate([silence, speech]), sr)
    good = v['responded']
    print(f'  [5] 어절 쉼 있는 말소리     → responded={v["responded"]}, latency={v["latency_ms"]}ms '
          + ('OK' if good else 'FAIL (말소리는 잡아야 함)'))
    ok &= good

    v = analyze_recording(fan, sr)
    good = not v['responded']
    print(f'  [6] 선풍기 소음만(5초)      → responded={v["responded"]} ' + ('OK (정상 소음은 무응답)' if good else 'FAIL'))
    ok &= good

    mixed = fan.copy()
    mixed[sr:sr + len(speech)] = np.clip(
        mixed[sr:sr + len(speech)].astype(np.int32) + speech.astype(np.int32),
        -32768, 32767).astype(np.int16)
    v = analyze_recording(mixed, sr)
    good = v['responded'] and abs(v['latency_ms'] - 1000) <= FRAME_MS * 4
    print(f'  [7] 선풍기 소음 위 말소리   → responded={v["responded"]}, latency={v["latency_ms"]}ms '
          + ('OK (소음 속에서도 감지)' if good else 'FAIL'))
    ok &= good

    # ── L2 내용 판정 (STT 엔진 없이 키워드 로직만 검증) ──
    cfg2 = {'stt': {'min_chars': 4}}
    weather = {'id': 'l1_weather', 'expect_any': ['날씨', '기온', '맑', '흐', '비', '눈', '구름']}
    free = {'id': 'l1_smalltalk'}
    l2_cases = [
        ('기대 키워드 일치', '오늘 서울 날씨는 맑고 기온은 28도입니다', weather, True),
        ('회피 표현 감지', '죄송해요, 잘 모르겠어요', weather, False),
        ('엉뚱한 답', '음악을 재생할게요', weather, False),
        ('자유 대화(내용 있음)', '저는 오늘 기분이 아주 좋아요', free, True),
        ('자유 대화(너무 짧음)', '네', free, False),
    ]
    for i, (name, text, scen, expect) in enumerate(l2_cases, start=8):
        v = stt.judge(text, scen, cfg2)
        good = v['passed'] == expect
        print(f'  [{i}] L2 {name:<18} → passed={v["passed"]} ({v["reason"]}) ' + ('OK' if good else 'FAIL'))
        ok &= good

    # ── 예약 슬롯 회피 (네트워크 없이 시간 판정만 검증) ──
    cfg3 = {'booking_avoidance': {'guard_before_minutes': 20, 'guard_after_minutes': 10}}
    avail = {'bookedSlots': [1], 'pendingCounts': {}, 'blockedSlots': [2]}
    day = datetime.date(2026, 8, 3)
    slot_cases = [
        ('1회차 진행 중(09:30)', datetime.time(9, 30), True),
        ('1회차 시작 15분 전(08:45)', datetime.time(8, 45), True),
        ('1회차 시작 40분 전(08:20)', datetime.time(8, 20), False),
        ('1회차 종료 5분 후(10:35)', datetime.time(10, 35), True),
        ('1회차 종료 30분 후(11:00)', datetime.time(11, 0), False),
        ('관리자 차단 2회차(13:30)', datetime.time(13, 30), True),
    ]
    for i, (name, t, expect_block) in enumerate(slot_cases, start=8 + len(l2_cases)):
        hit = booking.blocking_slot(cfg3, avail, datetime.datetime.combine(day, t))
        good = bool(hit) == expect_block
        state = '회피' if hit else '점검 가능'
        print(f'  [{i}] 슬롯 {name:<22} → {state} ' + ('OK' if good else 'FAIL'))
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
    p.add_argument('--transcribe', metavar='WAV', help='저장된 녹음으로 L2 내용 판정만 시험')
    p.add_argument('--scenario', metavar='ID', help='--transcribe에서 사용할 시나리오 ID')
    p.add_argument('--force', action='store_true', help='예약 시간대에도 강제로 점검 (시연 방해 주의)')
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
    if args.transcribe:
        cmd_transcribe(cfg, args.transcribe, args.scenario)
        return
    if args.once:
        run_all(cfg, force=args.force)
        return
    if args.loop:
        interval = float(cfg.get('loop_interval_minutes', 30))
        print(f'[loop] {interval:.0f}분 간격 주기 점검을 시작합니다. 중지: Ctrl+C')
        while True:
            if in_active_hours(cfg):
                run_all(cfg, force=args.force)
            else:
                print(f'[loop] 점검 시간대(active_hours={cfg.get("active_hours")}) 밖 — 이번 회차 건너뜀')
            time.sleep(interval * 60)

    p.print_help()


if __name__ == '__main__':
    main()
