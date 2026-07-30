#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
#  점검 문장 WAV 생성기 (Windows 전용)
#
#  Windows 내장 음성합성(SAPI)으로 점검 문장을 WAV 파일로 만든다.
#  한 번 만든 파일을 계속 재사용해야 점검 입력이 항상 동일해진다
#  (재현성 원칙 — DESIGN.md §5 참조).
#
#  사용법:
#    python synthesize_phrases.py "하이 엘지" phrases/wake.wav
#    python synthesize_phrases.py "지금 몇 시야?" phrases/ask_time.wav
#
#  ※ 한국어 음성(예: Microsoft Heami)이 설치돼 있어야 자연스럽다.
#    Windows 설정 → 시간 및 언어 → 음성 에서 한국어 음성 추가 가능.
#    합성 품질이 부족해 ThinQ ON이 인식하지 못하면, Windows '녹음기'
#    앱으로 사람 목소리를 직접 녹음해 같은 파일명으로 저장해도 된다.
# ============================================================

import os
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


def main():
    if len(sys.argv) != 3:
        print('사용법: python synthesize_phrases.py "문장" 출력파일.wav')
        print('예시  : python synthesize_phrases.py "지금 몇 시야?" phrases/ask_time.wav')
        sys.exit(1)
    if os.name != 'nt':
        sys.exit('[오류] 이 스크립트는 Windows 전용입니다. (Windows 내장 음성합성 사용)')

    text, out_path = sys.argv[1], os.path.abspath(sys.argv[2])
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

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


if __name__ == '__main__':
    main()
