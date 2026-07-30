# FieldCheck 점검 리그 — 노트북 설치 가이드 (구축 1단계)

> 처음 해보는 사람 기준으로 쓴 가이드입니다. 순서대로 따라 하면 됩니다.
> 이 프로그램이 하는 일: **저장된 점검 음성을 스피커로 재생 → ThinQ ON의 응답을 마이크로 녹음 → 응답이 왔는지/몇 초 걸렸는지 자동 판정 → 결과를 Google Sheets에 기록, 실패 시 담당자 메일.**

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
python synthesize_phrases.py "요즘 볼만한 영화 추천해줘" phrases/smalltalk.wav
python synthesize_phrases.py "오늘 날씨 어때?" phrases/ask_weather.wav
```
- 기동어("하이 엘지" 부분)는 **실제 ThinQ ON 기동어**로 바꿔서 만드세요.
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

## 문제 해결

| 증상 | 조치 |
|------|------|
| `python` 명령이 없다고 나옴 | Python 재설치하며 "Add to PATH" 체크 |
| 소리가 안 나옴 / 녹음이 안 됨 | `python fieldcheck.py --list-devices`로 장치 번호 확인 → `config.json`의 `output_device`/`input_device`에 번호 입력 |
| 항상 FAIL (응답하는데도) | 임계값이 너무 높음 → `voice_threshold_dbfs`를 5씩 낮춰보기 (예: -45 → -50) |
| 항상 OK (응답 없는데도) | 임계값이 너무 낮아 주변 소음을 응답으로 오인 → 5씩 올려보기, `--calibrate` 재실행 |
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
