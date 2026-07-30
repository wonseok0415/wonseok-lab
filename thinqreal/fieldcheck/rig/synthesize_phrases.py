#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
#  점검 문장 WAV 생성기 (Windows / macOS)
#
#  OS 내장 음성합성으로 점검 문장을 WAV 파일로 만든다.
#  - Windows: SAPI (한국어 음성 예: Microsoft Heami)
#  - macOS  : say 명령 (한국어 음성: Yuna)
#
#  한 번 만든 파일을 계속 재사용해야 점검 입력이 항상 동일해진다
#  (재현성 원칙 — DESIGN.md §5 참조).
#
#  사용법:
#    python synthesize_phrases.py "하이 엘지" phrases/wake.wav
#    python synthesize_phrases.py "지금 몇 시야?" phrases/ask_time.wav
#
#  ※ 합성 품질이 부족해 ThinQ ON이 인식하지 못하면, 녹음기 앱
#    (Windows '녹음기' / macOS 'QuickTime·음성 메모')으로 사람 목소리를
#    직접 녹음해 같은 파일명의 16-bit WAV로 저장해도 된다.
# ============================================================

import os
import re
import subprocess
import sys
import tempfile

PS_TEMPLATE = r'''
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer

# 한국어 음성이 있으면 우선 선택
$ko = $synth.GetInstalledVoices() | Where-Object {{ $_.VoiceInfo.Culture.Name -like 'ko*' }} | Select-Object -First 1
if ($ko) {{ $synth.SelectVoice($ko.VoiceInfo.Name) }}
else {{ Write-Warning '한국어 음성이 없어 기본 음성으로 합성합니다. (설정 > 시간 및 언어 > 음성 에서 한국어 추가 권장)' }}

$fmt = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(16000, [System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen, [System.Speech.AudioFormat.AudioChannel]::Mono)
$synth.SetOutputToWaveFile('{out}', $fmt)
$synth.Rate = -1   # 약간 천천히 (기동어 인식률에 유리)
$synth.Speak('{text}')
$synth.Dispose()
Write-Output ('저장 완료: ' + '{out}')
'''


def synth_windows(text, out_path):
    script = PS_TEMPLATE.format(text=text.replace("'", "''"), out=out_path.replace("'", "''"))
    with tempfile.NamedTemporaryFile('w', suffix='.ps1', delete=False, encoding='utf-8-sig') as f:
        f.write(script)
        ps1 = f.name
    try:
        r = subprocess.run(
            ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', ps1],
            capture_output=True, text=True)
        print(r.stdout.strip())
        if r.returncode != 0:
            print(r.stderr.strip())
            sys.exit('[오류] 음성 합성에 실패했습니다.')
    finally:
        os.unlink(ps1)


# macOS에 기본 탑재된 저품질 효과음성(다국어 장난감 음성) — 점검용으로 부적합
NOVELTY_VOICES = {
    'Albert', 'Bad News', 'Bahh', 'Bells', 'Boing', 'Bubbles', 'Cellos',
    'Eddy', 'Flo', 'Good News', 'Grandma', 'Grandpa', 'Jester', 'Organ',
    'Reed', 'Rocko', 'Sandy', 'Shelley', 'Superstar', 'Trinoids',
    'Whisper', 'Wobble', 'Zarvox',
}


def find_macos_korean_voice():
    try:
        listing = subprocess.run(['say', '-v', '?'], capture_output=True, text=True).stdout
    except FileNotFoundError:
        return None
    candidates = []
    for line in listing.splitlines():
        m = re.match(r'^(.*?)\s+(ko[_-]KR)\s', line)
        if m:
            candidates.append(m.group(1).strip())
    if not candidates:
        return None
    # 1순위: Yuna (자연스러운 한국어 음성)
    for name in candidates:
        if 'yuna' in name.lower() or '유나' in name:
            return name
    # 2순위: 장난감 음성이 아닌 것
    for name in candidates:
        base = name.split(' (')[0].strip()
        if base not in NOVELTY_VOICES:
            return name
    return None


def synth_macos(text, out_path):
    voice = find_macos_korean_voice()
    if not voice:
        print('[주의] 한국어 음성이 없어 기본 음성으로 합성합니다.')
        print('       시스템 설정 → 손쉬운 사용 → 콘텐츠 말하기 → 시스템 음성에서')
        print('       한국어(Yuna)를 다운로드하면 자연스러운 한국어 합성이 됩니다.')
    cmd = ['say']
    if voice:
        cmd += ['-v', voice]
    # 16 kHz / 16-bit WAV로 저장 (fieldcheck.py의 재생 포맷과 일치)
    cmd += ['-o', out_path, '--data-format=LEI16@16000', text]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr.strip())
        sys.exit('[오류] 음성 합성에 실패했습니다.')
    print('저장 완료: ' + out_path + (f'  (음성: {voice})' if voice else ''))


def main():
    if len(sys.argv) != 3:
        print('사용법: python synthesize_phrases.py "문장" 출력파일.wav')
        print('예시  : python synthesize_phrases.py "지금 몇 시야?" phrases/ask_time.wav')
        sys.exit(1)

    text, out_path = sys.argv[1], os.path.abspath(sys.argv[2])
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    if os.name == 'nt':
        synth_windows(text, out_path)
    elif sys.platform == 'darwin':
        synth_macos(text, out_path)
    else:
        sys.exit('[오류] Windows 또는 macOS에서 실행해 주세요. (OS 내장 음성합성 사용)')


if __name__ == '__main__':
    main()
