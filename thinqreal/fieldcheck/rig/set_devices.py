#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
#  config.json의 장치 지정을 안전하게 바꾸는 도구
#
#  긴 한 줄 python -c 명령을 손으로 옮겨 치다 생기는 오타 사고를 막기 위해
#  만들었다 (2026-08-21 Windows 셋업 중 실제 발생). rig 폴더에서 실행한다.
#
#  사용법:
#    python set_devices.py --show                  현재 값만 확인
#    python set_devices.py --camera 1              L3 카메라 번호 교체
#    python set_devices.py --mic UHD2160L          마이크를 이름으로 지정
#    python set_devices.py --camera 1 --mic UHD2160L   한 번에
#
#  장치 이름은 번호보다 안전하다 — 연결 순서·재부팅에 따라 번호는 바뀌지만
#  이름은 유지된다 (sounddevice가 이름 부분 일치를 지원).
#  이름 확인:  python -c "import sounddevice; print(sounddevice.query_devices())"
# ============================================================
import argparse
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(BASE, 'config.json')


def main():
    p = argparse.ArgumentParser(description='config.json 장치 지정 변경 (rig 폴더에서 실행)')
    p.add_argument('--camera', type=int, help='L3 카메라 번호 (모든 L3 시나리오에 적용)')
    p.add_argument('--mic', help='입력 장치 이름 (예: UHD2160L)')
    p.add_argument('--speaker', help='출력 장치 이름 (기본 출력을 쓰면 지정 불필요)')
    p.add_argument('--show', action='store_true', help='현재 값만 표시하고 종료')
    a = p.parse_args()

    if not os.path.exists(PATH):
        raise SystemExit('[오류] config.json이 없습니다 — rig 폴더에서 실행했는지 확인해 주세요.')
    with open(PATH, encoding='utf-8') as f:
        cfg = json.load(f)

    changed = False
    if a.camera is not None:
        n = 0
        for s in cfg.get('scenarios', []):
            if 'camera' in s:
                s['camera']['device'] = a.camera
                n += 1
        print(f'카메라 번호 → {a.camera} (L3 시나리오 {n}개에 적용)')
        changed = True
    if a.mic is not None:
        cfg['input_device'] = a.mic
        print(f'입력 장치(마이크) → {a.mic}')
        changed = True
    if a.speaker is not None:
        cfg['output_device'] = a.speaker
        print(f'출력 장치(스피커) → {a.speaker}')
        changed = True

    if changed:
        with open(PATH, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        print('저장 완료.')
    elif not a.show:
        p.print_help()

    print('현재 설정:')
    print('  마이크(input_device)  =', cfg.get('input_device'))
    print('  스피커(output_device) =', cfg.get('output_device'))
    print('  L3 카메라 번호        =',
          [s['camera'].get('device') for s in cfg.get('scenarios', []) if 'camera' in s])


if __name__ == '__main__':
    main()
