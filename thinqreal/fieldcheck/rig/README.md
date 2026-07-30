# FieldCheck 점검 리그 — 노트북 설치 가이드 (구축 1단계)

> 처음 해보는 사람 기준으로 쓴 가이드입니다. 순서대로 따라 하면 됩니다.
> 이 프로그램이 하는 일: **저장된 점검 음성을 스피커로 재생 → ThinQ ON의 응답을 마이크로 녹음 → 응답이 왔는지/몇 초 걸렸는지 자동 판정 → 결과를 Google Sheets에 기록, 실패 시 담당자 메일.**
>
> **Windows와 맥 모두 지원**합니다. 최초 점검(개발자 작업 PC = 맥북)은 아래 [맥에서 실행하기]를 참고하고, 상주 리그(Windows 노트북)는 본문 순서대로 진행하세요.

## 0. 준비물

- Windows 노트북 1대 (내장 스피커·마이크 사용)
- ThinQ Real 공간의 사외망 Wi-Fi 연결
- 이 폴더(`rig/`) 전체를 노트북에 복사 (GitHub에서 ZIP 다운로드 또는 USB 복사)

## 1. Python 설치 (딱 한 번)

1. https://www.python.org/downloads/ 에서 최신 버전 다운로드
2. 설치 첫 화면에서 **"Add python.exe to PATH" 체크박스를 반드시 체크** 후 Install Now
3. 설치 확인: 시작 메뉴 → `cmd` 입력 → 명령 프롬프트 열기 → 아래 입력
   ```
   python --version
   ```
   `Python 3.x.x`가 나오면 성공

## 2. 필요 프로그램 설치 (딱 한 번)

명령 프롬프트에서 이 폴더로 이동한 뒤 설치:
```
cd C:\fieldcheck\rig        ← 실제 복사해 둔 경로로
pip install sounddevice numpy
```

## 3. 설정 파일 만들기 (딱 한 번)

1. `config.example.json`을 복사해서 같은 폴더에 `config.json`으로 저장
2. 메모장으로 열어 두 값 확인:
   - `endpoint_url` — Apps Script 주소 (기본값이 현재 운영 주소)
   - `api_key` — Apps Script의 `FC_API_KEY`와 같은 값이어야 함

## 4. 점검 음성 만들기 (딱 한 번)

Windows 내장 음성합성으로 점검 문장을 WAV 파일로 만듭니다:
```
python synthesize_phrases.py "하이 엘지" phrases/wake.wav
python synthesize_phrases.py "지금 몇 시야?" phrases/ask_time.wav
python synthesize_phrases.py "오늘 기분 어때?" phrases/smalltalk.wav
python synthesize_phrases.py "오늘 날씨 어때?" phrases/ask_weather.wav
```
- 기동어("하이 엘지" 부분)는 **실제 ThinQ ON 기동어**로 바꿔서 만드세요.
- **명령 문장 앞에 기동어를 붙이지 마세요.** 프로그램이 기동어 파일을 먼저 재생하고, ThinQ ON이 '띵' 하고 반응할 시간(`wake_gap_seconds`, 기본 1.2초)을 기다린 뒤 명령을 재생합니다. 명령이 앞부분부터 씹히면 이 값을 1.5~2.0으로 올려보세요 (config.json).
- 합성 음성을 ThinQ ON이 인식하지 못하면: Windows **녹음기 앱**으로 사람 목소리를 직접 녹음해서 같은 파일명(`phrases/wake.wav` 등)으로 저장하면 됩니다.
- **중요**: 한 번 만든 파일은 바꾸지 마세요. 매번 같은 음성이 재생되어야 "오늘 실패가 ThinQ ON 문제"라고 말할 수 있습니다.

## 5. 자리 잡기 + 소음 측정

1. 노트북을 ThinQ ON에서 1~2m 거리에 두고 전원을 연결
2. 주변 소음 측정:
   ```
   python fieldcheck.py --calibrate
   ```
   추천 임계값이 나오면 `config.json`의 `voice_threshold_dbfs`에 입력

## 6. 첫 점검 실행

```
python fieldcheck.py --once
```
- 스피커에서 점검 음성이 나오고, ThinQ ON이 대답하면 `[OK ]`, 무응답이면 `[FAIL]`이 표시됩니다.
- 결과는 Google Sheets `health_checks` 탭에 자동 기록됩니다.
- 기동어 인식이 안 되면: 노트북 **볼륨을 조금씩 올리며** `--once`를 반복 → 잘 되는 볼륨을 찾은 뒤 **그 볼륨으로 고정** (이후 변경 금지)

## 7. 주기 점검 시작

```
python fieldcheck.py --loop
```
- `config.json`의 `loop_interval_minutes`(기본 30분) 간격으로 자동 반복합니다.
- `active_hours`(기본 07:00–19:00) 밖의 시간에는 발화하지 않습니다.
- 창을 닫으면 중지됩니다. 상시 운영 시에는 창을 열어 둔 채 노트북 덮개만 닫으세요 (아래 8번 설정 필수).

## 8. 노트북 상시 가동 설정 (딱 한 번)

1. 설정 → 시스템 → 전원: "덮개를 닫으면" → **아무 것도 안 함**
2. 같은 화면에서: 전원 연결 시 절전 모드 → **안 함**
3. Windows 업데이트 → 사용 시간 설정: 점검 시간대(07~19시)를 사용 시간으로 지정

## 맥에서 실행하기 (최초 점검용)

맥북에서 먼저 테스트할 때는 위 1~7번 대신 이렇게 하면 됩니다:

1. **Python**: 맥에는 `python3`가 이미 있습니다. 터미널에서 `python3 --version`으로 확인 (없으면 실행 시 설치 안내가 뜹니다)
2. **설치**: 저장소 클론 후
   ```
   cd wonseok-lab/thinqreal/fieldcheck/rig
   pip3 install sounddevice numpy
   ```
3. **한국어 음성 준비 (권장)**: 시스템 설정 → 손쉬운 사용 → 콘텐츠 말하기 → 시스템 음성 → 한국어 **Yuna** 다운로드
4. **점검 음성 생성**: Windows와 동일한 명령을 `python3`로 실행
   ```
   python3 synthesize_phrases.py "하이 엘지" phrases/wake.wav
   python3 synthesize_phrases.py "지금 몇 시야?" phrases/ask_time.wav
   python3 synthesize_phrases.py "오늘 기분 어때?" phrases/smalltalk.wav
   python3 synthesize_phrases.py "오늘 날씨 어때?" phrases/ask_weather.wav
   ```
5. **설정·소음 측정·점검**: 본문 3, 5, 6번과 동일 (`python` 대신 `python3`)
6. **마이크 권한**: 첫 녹음 시 "터미널(또는 VS Code)이 마이크에 접근하려고 합니다" 창이 뜨면 **허용**. 지나쳤다면 시스템 설정 → 개인정보 보호 및 보안 → 마이크에서 터미널/VS Code를 켜기

맥에서 만든 `phrases/*.wav`는 Windows 리그에서도 그대로 재생됩니다. 다만 **재현성 원칙**상, 상주 리그를 Windows 노트북으로 옮기는 시점에 어느 파일 세트를 최종본으로 쓸지 정하고 이후에는 바꾸지 마세요.

## dBA 보정 (선택 — 숫자를 실제 소음계와 맞추기)

점검 출력의 "소음 바닥 / 최고" 값은 **A-가중(dBA)** 측정입니다. 다만 노트북 마이크는 교정된 소음계가 아니라서, 보정 전에는 **상대값**으로 표시됩니다 (판정 정확도에는 영향 없음 — 판정은 바닥 대비 차이만 사용).

실제 소음계 숫자처럼 보고 싶으면 한 번만 보정하세요:

1. 휴대폰에 소음측정 앱 설치 (예: "Sound Meter", 데시벨 측정기)
2. `python3 fieldcheck.py --calibrate` 실행 — 표시값 확인 (예: `-38.2 dBA (상대값)`)
3. 같은 자리·같은 시점에 휴대폰 앱으로 측정 (예: `47 dBA`)
4. `config.json`에 차이를 입력: `"dba_calibration_offset": 85.2` ← 47 − (−38.2)
5. 이후 모든 출력·기록이 실측 근사 dBA로 표시됩니다

## 문제 해결

| 증상 | 조치 |
|------|------|
| `python` 명령이 없다고 나옴 | Python 재설치하며 "Add to PATH" 체크 |
| 소리가 안 나옴 / 녹음이 안 됨 | `python fieldcheck.py --list-devices`로 장치 번호 확인 → `config.json`의 `output_device`/`input_device`에 번호 입력 |
| 항상 FAIL (응답하는데도) | 응답 판정은 소음 바닥 대비 상대 기준(`voice_over_floor_db`, 기본 8) — 8→5로 낮추거나, 노트북을 ThinQ ON에 더 가까이 배치. 실행 시 출력되는 "판정 참고: 소음 바닥/최고" 값에서 최고가 바닥+8을 넘는지 확인 |
| 항상 OK (응답 없는데도) | `voice_over_floor_db`를 8→12로 올려보기 |
| 에어컨·선풍기 소음 환경 | 자동 대응됨 — 음성 대역(250~4000Hz)만 측정하고 소음 바닥에 자동 적응. `voice_threshold_dbfs`(`--calibrate`)는 '응답 종료 대기'에만 사용 |
| 서버 전송 실패 표시 | Wi-Fi 확인. 전송이 실패해도 `results.jsonl`에 로컬 기록은 남습니다 |
| 판정 로직이 의심될 때 | `python fieldcheck.py --selftest` (오디오 장치 없이 검증) |

## 파일 안내

| 파일 | 역할 |
|------|------|
| `fieldcheck.py` | 메인 프로그램 |
| `synthesize_phrases.py` | 점검 문장 WAV 생성기 |
| `config.json` | 내 설정 (커밋 금지 — api_key 포함) |
| `phrases/` | 점검 음성 파일 (한 번 만들고 고정) |
| `recordings/` | ThinQ ON 응답 녹음 (실패 원인 확인용) |
| `results.jsonl` | 전체 점검 로그 (서버 전송 실패 대비 로컬 백업) |
| `state.json` | 연속 실패 카운트 (메일 발송 판단용) |
