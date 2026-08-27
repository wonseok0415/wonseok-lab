# LG AX 해커톤 — ThinQ Real AI Field Ops (세션 인수인계)

> 이 문서는 「thinq-real-reservation-system」 세션(2026-08-26~27)의 작업 맥락을 다른 Claude Code 세션
> (예: '[NEW]thinqreal - 도메인 이전')에 전달하기 위한 인수인계 기록이다.
> 이 `hackathon/` 트랙은 해커톤 출품 준비 전용이며, 메인 시스템·FieldCheck·ideas 트랙을 수정하지 않는다 (순수 추가).

## 1. 무엇을 하고 있나

- 사용자(강원석)가 **사내 LG AX 해커톤**에 출품 준비 중.
- 출품 주제: **ThinQ Real AI Field Ops** — ThinQ Real 예약 관리 시스템 위에 AI Agent 레이어를 얹는 제안.
- 지원서는 사내 포털 웹폼(총 8개 섹션)으로 작성하며, 초안은 사내 AI 툴(GPT 계열)과 병행 작성 중.
- 실서비스 소스는 `wonseok0415/thinqreal` 저장소 (라이브: thinqreal.com). 이 세션은 해당 리포를 읽기 전용으로
  클론해 컨텍스트를 파악했다. 예약 시스템·설문 파이프라인·월간 리포트·ROI 툴·FieldCheck 현황은
  그 리포의 `CLAUDE.md`가 단일 소스.

## 2. 지원서 작성 현황 (사용자가 스크린샷으로 공유한 범위)

### 섹션 2 — 서비스 정의
- AI서비스(Agent)명: **ThinQ Real AI Field Ops** / 업무 분야: **개발(SW)**
- 한 줄 요약: "ThinQ Real의 예약 정보와 현장 대화, ThinQ ON 자동 점검 데이터를 통합 분석하여
  방문 준비부터 고객 인사이트 및 운영 리포트 생성까지 지원하는 AI Agent입니다."

### 섹션 3 — 문제정의 (Pain Point 4가지)
1. 예약 데이터는 있으나 방문 준비(시연 시나리오·준비물·안내)는 담당자 수동 판단.
   현장 고객 반응은 도슨트 기억·사후 설문 의존 → 고객 목소리 미축적 (3/24 이후 22건 방문 근거).
2. ThinQ ON 음성 응답·서비스 상태를 사람이 사전 확인해야 함 — 2026년 7월 무응답 장애를
   반나절 늦게 발견한 실사례 인용.
3. 예약·설문·ROI·대화·점검 데이터가 방문 건 단위로 연결되지 않아 월간 보고를 수작업 재정리.
4. 생성형 AI로 직접 구축했으나 사내 AI 툴 사용량·접근 환경 제약으로
   개인 계정↔사내 계정 간 컨텍스트 수동 전달 반복.

### 섹션 3 — 문제의 중요성 (정량 근거)
- 연간 운영비 0.73억 / 2026년 6월 한 달 20건·127명 방문.
- 기존 ROI 분석: 연간 창출 가치 약 1.84억, 투자 회수 1년 11개월 (시나리오 기반 추정 → 실데이터 검증 필요 논리).
- 시연 실패 1회가 제품·AI홈 솔루션 전반 신뢰 훼손 리스크.

### AS-IS → TO-BE 다이어그램 (웹폼 내 표 편집기)
- AS-IS 4단계(수동 방문 준비 / 현장 대화 미축적 / ThinQ ON 수동·사후 확인 / 운영 데이터 개별 확인·보고서 재작성)를
  TO-BE 3개 Agent로 재편: ① 방문 준비 Agent(빨강) ② 현장 인사이트·품질 Agent(파랑, AS-IS 2·3 통합) ③ 통합 운영·리포트 Agent(주황).

## 3. 이 세션의 산출물 — AI 서비스 구조도 (섹션 내 이미지 업로드용)

웹폼 요구: **가로 860px JPG**. 사내 AI가 잡은 알고리즘(아래 5계층)을 기반으로 이 세션에서 이미지 제작 완료.

```
[입력 데이터] 예약 정보 / 현장 대화 녹음 / 방문 후기 설문 / ThinQ ON 응답 녹음·응답시간 / 웹캠 기반 가전 동작 결과
→ [수집·전처리 계층] 예약 ID 기반 데이터 연결 / 개인정보·권한 처리 / 음성 품질 확인 / STT
→ [ThinQ Real AI Field Ops] 방문 준비 Agent / 현장 인사이트 Agent / 품질 판정 Agent / 운영 리포트 Agent
→ [Human-in-the-Loop] 근거 확인 / 불확실 결과 검토 / 리포트 승인
→ [출력] 방문 전 브리핑 / 고객 인사이트 / ThinQ ON 이상 알림 / 후속 액션 아이템 / 월간 운영·ROI 리포트
```

### 파일 (이 폴더 `diagram/`)
| 파일 | 용도 |
|---|---|
| `structure_diagram_860px.jpg` (860×772) | 웹폼 규격 제출용 |
| `structure_diagram_1720px.jpg` (1720×1544) | 2배 해상도 원본 — 폼이 자동 축소를 지원하면 이쪽 업로드 권장, 발표 자료 재사용용 |
| `structure_diagram.html` | 원본 소스 — 문구·색·배치 수정 후 재렌더링 가능 |

### 디자인 결정 사항
- 5단 좌→우 흐름, Agent 4색 구분: 방문 준비 `#c5473f`(빨강) / 현장 인사이트 `#3563a8`(파랑) /
  품질 판정 `#22766e`(청록) / 운영 리포트 `#c07a2c`(주황). **출력 박스 왼쪽 색 띠 = 담당 Agent 색** (범례 하단 표기).
- 지원서의 AS-IS/TO-BE 다이어그램 색 구분(빨강/파랑/주황)과 연속성 유지.
- 테두리·강조는 ThinQ Real 브랜드 컬러 다크 올리브 `#3a5035`.
- Human-in-the-Loop는 점선 박스 — AI 산출물이 담당자 검토·승인을 거친다는 안전장치 표현.
- "예약 건(ID) 단위 연결"을 부제 + 하단 데이터 키 문구로 강조 (Pain Point 3에 대한 답).
- 1차본이 글자가 작아 가독성 지적받음 → 폰트 전면 확대(박스 제목 13px 등)한 현재본이 최종.

### 재렌더링 방법 (클라우드 세션 기준)
```bash
# 한글 폰트 필요: apt-get install -y fonts-noto-cjk  /  변환: pip install pillow
CHROME=$(find /opt/pw-browsers/chromium* -name chrome | head -1)
"$CHROME" --headless --no-sandbox --disable-gpu --force-device-scale-factor=2 \
  --window-size=860,1200 --hide-scrollbars --screenshot=out_2x.png structure_diagram.html
# 이후 PIL로: 흰 배경 bbox 크롭(+여백 28px) → 1720px 저장 → 860px 리사이즈(LANCZOS) 저장, quality=95
```

## 4. 남은 일 / 참고

- 지원서 나머지 섹션(서비스 상세 설명, 4/8 이후)은 미공유 상태 — 이어서 도울 때 스크린샷·텍스트 요청.
- 수치 인용 시 출처: 방문 통계·ROI 수치는 `wonseok0415/thinqreal`의 관리자 대시보드·ROI 툴 기준.
  **민감 단가·실데이터 커밋 금지 규칙**(thinqreal CLAUDE.md §보안)은 이 트랙에도 동일 적용 —
  이 문서에는 총액 요약 수준(0.73억/1.84억 등, 지원서에 이미 쓴 값)만 기재했다.
- 이 브랜치: `claude/thinq-real-reservation-system-egrfud` (wonseok0415/wonseok-lab).
