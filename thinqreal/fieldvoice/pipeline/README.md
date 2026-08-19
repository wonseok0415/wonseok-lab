# FieldVoice 파이프라인 — 설치·운영 가이드 (초보자용)

인터뷰 녹음(또는 전사 텍스트)을 넣으면 **전사 → 화자 라벨링 → 요약 → 맥락 분석 →
인사이트 도출 → 파일 저장**까지 자동으로 돌아가는 도구다. 웹 UI에서 파일을 올리고
결과를 열람한다. 설계 배경은 상위 폴더의 `DESIGN.md` 참조.

## 0. 개인정보 먼저 (반드시 읽기)

- 녹음·전사·리포트는 전부 이 폴더의 `uploads/`, `output/`에만 저장된다.
  `.gitignore`로 커밋이 차단돼 있지만, **어떤 경로로든 저장소·메신저에 올리기 전에
  가명화·동의 상태를 확인**한다 (DESIGN.md §5).
- 전사는 로컬 Whisper(음성이 컴퓨터 밖으로 안 나감), 분석은 전사 **텍스트**가
  Claude API로 전송된다. 실고객 녹음을 분석하기 전에 동의서에 이 처리 방식이
  포함되어 있는지 확인할 것.

## 1. 실행 (맥북)

```
cd ~/workspace/wonseok-lab/thinqreal/fieldvoice/pipeline
```

```
bash run.sh
```

처음 실행이면 가상환경 생성과 설치로 1~2분 걸린다. 브라우저가 자동으로 열린다
(`http://127.0.0.1:8765`). 종료는 터미널에서 `Ctrl+C`.

## 2. 분석 백엔드 (최초 1회)

분석 에이전트가 Claude를 호출하는 경로는 두 가지 — 기본 설정(auto)이 자동으로 고른다:

- **경로 A — Claude Code CLI (권장, 추가 비용 없음)**: Claude 구독(Pro/Max)에 포함된
  Claude Code를 분석 엔진으로 사용한다. 맥에 Claude Code가 설치·로그인되어 있으면
  **할 일이 없다** — 확인만:

```
claude --version
```

- **경로 B — Claude API 크레딧 (과금)**: platform.claude.com(구 console)에서 크레딧
  구매 + 키 발급 후 실행 전에:

```
export ANTHROPIC_API_KEY=발급받은키
```

  키를 코드·config·저장소에 적지 않는다 (FieldCheck의 Script Properties 원칙과 동일).
  API 경로는 프롬프트 캐시·스트리밍 등이 켜져 있어 대량·정기 운영에 유리하다.

속도·품질 차이: 두 경로 모두 같은 프롬프트를 쓰며 품질은 동급. A는 구독 사용량
한도를 소모하고, B는 크레딧을 소모한다. 파일럿·개인 사용은 A로 충분하다.

## 3. 오디오 전사(STT)까지 쓰려면 (선택)

전사 텍스트(.txt)만 다룰 거면 건너뛴다. 오디오 파일을 직접 올리려면:

```
./venv/bin/pip install faster-whisper
```

첫 전사 때 Whisper 모델을 자동 다운로드한다(수백 MB~1GB대, 이후 오프라인 동작).
기본 모델은 `medium`(현장 검토 결과 채택) — 전사가 너무 오래 걸리면 `config.json`에서
`whisper_model`을 `"small"`로 (2~3배 빠름, 고유명사 오인식은 늘어남).

## 4. 사용법

1. 웹 UI에서 오디오(wav·mp3·m4a 등) 또는 전사 텍스트(.txt) 업로드 → **분석 시작**
2. 6단계 진행 상황이 실시간으로 표시됨 (90분 녹음 기준: 전사 수 분~수십 분,
   분석 단계는 합쳐서 수 분)
3. 완료되면 탭으로 결과 열람: **통합 리포트 / 인사이트 / 맥락 분석 / 요약 / 라벨 전사 / 원본 전사**
4. 파일은 `output/<세션>/`에 마크다운으로 저장 — `report.md`가 공유용 통합본
5. 처음이면 **"샘플 전사로 시험"** 버튼으로 전체 흐름을 먼저 확인 (가상 인터뷰 데이터,
   오디오·STT 불필요, API 인증만 있으면 됨)

명령줄로도 가능:

```
./venv/bin/python pipeline.py 녹음파일.m4a
```

## 5. 설정 (선택)

`config.example.json`을 `config.json`으로 복사해 수정 (없으면 example 값 사용):

| 항목 | 기본값 | 설명 |
|---|---|---|
| `llm_backend` | `auto` | `auto`(API 키 있으면 api, 아니면 claude_cli) / `api` / `claude_cli` |
| `model` | `claude-opus-5` | 분석 모델 (api 백엔드용) |
| `claude_cli_model` | (비움) | claude_cli 백엔드 모델 지정 (비우면 Claude Code 기본 모델) |
| `whisper_model` | `medium` | STT 모델 — 현장 검토 결과 기본을 `medium`으로 (더 정확). 속도가 급하면 `small`(약 2~3배 빠름, 오인식 증가) |
| `vocabulary_hint` | ThinQ 등 | STT 고유명사 힌트 (FieldCheck 선례 — 첫 실녹음 오인식 실측 반영) |
| `whisper_condition_on_previous_text` | `false` | `false`면 환청 반복 루프 완화 (기본 유지 권장) |
| `port` | `8765` | 웹 UI 포트 |

## 6. 문제 해결

| 증상 | 원인·조치 |
|---|---|
| "분석 백엔드가 없습니다" | §2 — Claude Code CLI 설치·로그인(무료 경로)이 가장 간단 |
| "Claude CLI 오류" | 터미널에서 `claude` 단독 실행 → 로그인 상태 확인 후 재시도 |
| "API 인증 실패" (api 백엔드) | §2 경로 B — 키·크레딧 확인 |
| "faster-whisper가 설치되어 있지 않습니다" | §3 설치, 또는 .txt로 우회 |
| 전사에 이상한 단어 | `config.json`의 `vocabulary_hint`에 해당 고유명사 추가 |
| 전사에 "(위 발화가 …회 반복됨)" 표기 | 정상 — 무음·기계음 구간의 STT 환청을 자동 압축한 것 |
| 포트 충돌 (주소가 이미 사용 중) | `config.json`에서 `port` 변경 |
| 화자 라벨이 뒤섞임 | 1채널 한계 — 라벨 전사 탭에서 확인 후 수동 교정, 장기적으론 채널 분리 마이크 (DESIGN.md §6) |

## 7. 구조

```
pipeline.py     오케스트레이터 (단계 실행·저장·CLI)
transcribe.py   전사 — 로컬 faster-whisper
agents.py       LLM 에이전트 4종 (라벨링·요약·맥락·인사이트)
webapp.py       웹 UI (Flask, 로컬 전용)
run.sh          원클릭 실행
sample/         샘플 전사 (가상 데이터 — 시험용)
uploads/ output/  업로드·결과 (자동 생성, 커밋 금지)
```
