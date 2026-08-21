# 공용 노트북(Windows) 통합 셋업 체크리스트 — FieldCheck 이전 + 공용 운영

> **v1.0 (2026-08-19)** · 대상 장비: 팀원 기증 Windows 노트북 (사내 보안 프로그램 미설치,
> ThinQ Real 쇼룸 상주, 사용 권한 = 관리자 3인)
> 이 장비의 역할 두 가지: **① FieldCheck 아침 자동 점검** (이 문서가 다루는 이전 작업)
> **② FieldVoice 시연 녹음·전사** (공통 항목만 여기 포함 — 세부는 `../fieldvoice/OPERATIONS.md`)
> 순서대로 진행하면 된다. ⏱ 예상 소요: A~B 30분, C 60~90분(모델 다운로드 포함), D 하루(익일 검증).

## A. 보안·계정 (가장 먼저 — 데이터를 올리기 전에)

- [ ] **A1. 운영 전용 로컬 계정 생성** — 기증자 개인 계정은 제거/비활성. 계정 이름 예: `thinqreal`,
      로그인 암호 설정 (관리자 3인 공유)
- [ ] **A2. 디스크 암호화 → 대체 방안으로 확정 (2026-08-21)** — 이 장비는 **Windows Home +
      2013년 기종(TPM 미지원)이라 BitLocker·장치 암호화 모두 불가**로 확인됨. 대체 조치:
      - **민감 데이터 무보관 원칙 강화**: FieldVoice 녹음 원본은 당일 전사 → **당일 파기**
        (이 장비는 30일 보관 불가 장비로 규정). FieldCheck config의 FC_API_KEY는 유출 시
        Script Property에서 즉시 교체 가능한 저위험 — 감수
      - **켄싱턴 와이어 락**으로 은닉 위치 가구에 물리 고정 (스피커와 함께 구매)
- [ ] **A3. 자동 로그인 + 자동 잠금 (키오스크 패턴)** — 정전·재부팅 후 로그인 화면에서 멈춰
      점검이 안 도는 사고(macOS에서 실제 발생)의 Windows판 예방:
      - `netplwiz` 실행 → "사용자 이름과 암호를 입력해야 함" 체크 해제 (자동 로그인)
      - 화면 잠금: 설정 → 계정 → 로그인 옵션에서 잠금 시간 설정. 잠긴 상태에서도 로그온 세션은
        유지되므로 점검·녹음은 계속 동작한다 (D 단계에서 실제 확인)
      - 자동 로그인의 보안 공백은 A2(암호화)+즉시 잠금이 메운다
- [ ] **A4. 보관 최소화 규칙 합의 (관리자 3인)** — 녹음 원본은 전사 검수 후 즉시 파기,
      개인 파일 저장 금지, 이 장비에 개인 Claude·GitHub 계정 로그인 금지
      (GitHub는 공개 저장소라 clone/pull에 로그인 불필요 — push는 개인 장비에서)

> **디스크 암호화 vs 로그인 암호 — 뭐가 다른가**
> 로그인 암호는 "켜져 있는 Windows"로 들어오는 문만 잠근다. 노트북을 훔쳐 디스크를 뽑아
> 다른 PC에 꽂으면 암호 없이 파일이 전부 읽힌다. 디스크 암호화는 저장된 데이터 자체를
> 암호문으로 만들어 그 경로를 차단한다. **사용감은 평소와 동일** — TPM 칩이 있는 기종은
> 부팅 시 추가 암호 입력도 없고, 늘 하던 로그인만 하면 된다. 성능 영향도 체감 안 되는 수준.

## B. 상시 가동·전원 (FieldCheck DESIGN §4 + 공용 운영 R6)

- [ ] **B1. 전원 연결 상시 유지** + 절전 끄기: 설정 → 시스템 → 전원 → "전원 연결 시 절대 안 함"
      (화면 끄기는 무방, 절전만 금지)
- [ ] **B2. 덮개 닫아도 계속 실행**: 전원 옵션 → 덮개를 닫을 때 → "아무 것도 안 함" (전원 연결 시)
- [ ] **B3. Windows 업데이트 재부팅 시간 통제**: 설정 → Windows 업데이트 → 사용 시간
      (06:00~18:00으로 지정 → 재부팅은 그 밖 새벽에만). 두 시스템의 금지 창(07:00 점검,
      09:00~16:30 슬롯)을 모두 피하게 됨
- [ ] **B4. 볼륨 고정 + 물리 라벨 부착**: 점검이 잘 되는 볼륨으로 맞춘 뒤 스티커 부착 —
      "이 장비는 ① 아침 자동 점검 ② 시연 녹음 중 — 끄지 말 것, 볼륨 건드리지 말 것"
      (볼륨 저하로 점검 전체가 흔들린 사고 선례. 스피커 자가 진단이 잡아주지만 예방이 우선)
- [ ] **B5. 마이크·카메라 개인정보 설정 확인**: 설정 → 개인 정보 및 보안 → 마이크/카메라 →
      "데스크톱 앱이 액세스하도록 허용" 켬 (macOS TCC 함정의 Windows판 — 여기는 화면에서
      바로 켤 수 있어 간단)

## C. FieldCheck 이전 (점검 장비 역할 설치)

- [ ] **C1. Python 설치** — python.org에서 3.11 이상, 설치 시 **"Add python.exe to PATH" 체크 필수**
- [ ] **C2. 저장소 받기** (PowerShell):

      git clone https://github.com/wonseok0415/wonseok-lab.git C:\workspace\wonseok-lab

      git 미설치면 git-scm.com에서 먼저 설치. 이후 갱신은 `git pull`만 (push 금지 — A4)
- [ ] **C3. 패키지 설치**:

      pip install sounddevice numpy opencv-python faster-whisper

- [ ] **C4. config.json 이전** — 맥북의 `rig/config.json`을 **USB 메모리로 복사**
      (api_key가 들어 있으므로 메일·메신저 전송 금지). 붙여넣을 위치:
      `C:\workspace\wonseok-lab\thinqreal\fieldcheck\rig\config.json`
- [ ] **C5. 음성 파일 이전** — 맥북의 `rig/phrases/` 폴더 전체를 같은 방법(USB)으로 복사
      (사람 녹음 WAV는 저장소에 없음 — 잊으면 점검이 시작부터 실패)
- [ ] **C6. 마이크 확인 + dBA 재보정** — **마이크가 바뀌었으므로 보정값은 맥북 값(87.4)을 쓰면 안 됨**:

      cd C:\workspace\wonseok-lab\thinqreal\fieldcheck\rig

      python fieldcheck.py --mic-test

      휴대폰 소음 앱과 대조해 `dba_calibration_offset` 재교정 (절차: rig/README §dBA 보정.
      판정 자체는 상대 기준이라 보정 전에도 정확 — 표시 숫자만 어긋남)
- [ ] **C7. 웹캠 연결 + 영역 확인** — 삼각대 구도가 맥북 검증 때와 같으면 맥북의
      `rig/camera_roi.json`을 USB로 복사하면 끝. 구도가 바뀌었으면 재지정:

      python vision.py --snapshot --device 1

      python vision.py --pick --device 1

      (장치 번호는 --snapshot으로 웹캠 화면이 나오는 번호를 찾는다 — 0은 내장)
- [ ] **C8. 수동 검증**:

      python fieldcheck.py --selftest

      python fieldcheck.py --once --force

      전 시나리오(L1·L2·L3) 통과 + 서버 전송 성공 확인 (첫 실행은 Whisper 모델 다운로드로 오래 걸림)
- [ ] **C9. 자동 실행 등록** (기본 07:00):

      powershell -ExecutionPolicy Bypass -File schedule\install_windows.ps1

- [ ] **C10. 잠금 상태 동작 확인** — 화면을 잠근 채(Win+L):

      Start-ScheduledTask -TaskName "ThinQReal FieldCheck"

      스피커에서 점검 발화가 나오고 판정이 진행되면 통과 (로그: `logs\schedule.log`)

## D. 전환 완료 게이트 (모두 통과해야 이전 종료)

- [ ] **D1. 익일 07:00 자동 실행 확인** — `logs\schedule.log`에 07:00 타임스탬프 + 요약 메일 도착
- [ ] **D2. 맥북 쪽 자동 점검 해제** — ⚠ **두 장비가 동시에 말을 걸면 서로의 점검을 오염**시키므로
      D1 통과 즉시 맥북에서:

      bash schedule/uninstall_macos.sh

      sudo pmset repeat cancel

- [ ] **D3. 맥북의 기존 녹음·스냅샷 정리** — recordings/는 증거 보존 차원에서 당분간 맥북에 유지
      (공용 장비로 옮기지 않음), 이후 보관 기한은 컴플라이언스 확인과 함께 결정

## E. FieldVoice 공통 확인 (세부는 `../fieldvoice/OPERATIONS.md`)

- [ ] E1. 전사는 **그날 시연 종료 후** 실행 (2026-08-19 사용자 확정 — 07:00 점검 창과 자연 회피)
- [ ] E2. 분석은 개인 맥북에서 (공용 장비에 개인 Claude 계정 로그인 금지 — A4와 동일 원칙)
- [x] E3. `run.bat`(Windows용 실행 스크립트) — FieldVoice 트랙에서 구현 완료 (2026-08-20 확인, `../fieldvoice/pipeline/run.bat`)
