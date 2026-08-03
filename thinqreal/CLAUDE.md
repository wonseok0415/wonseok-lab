# ThinQ Real 운영관리 웹사이트

> ## ⚠ 필독 — 실서비스 소스는 이 저장소가 아님 (2026-07-30 확인)
> thinqreal.com 도메인 이전이 **완료**되어, 예약 관리 시스템의 실서비스 소스는
> **`wonseok0415/thinqreal` 저장소**(루트 구조)로 옮겨갔다. 이 저장소의
> `thinqreal.html` / `thinqreal_admin.html` / `ThinQReal_AppScript.gs`는 **구버전 사본**이다.
> - 실서비스 Apps Script: `wonseok0415/thinqreal` 루트의 `ThinQReal_AppScript.gs` (3,700줄+, 인증·텔레그램·설문 등 대폭 확장됨)
> - **이 저장소의 .gs를 script.google.com에 배포하면 운영 장애 발생** — 파일 내용은 안내문으로 교체해 둠
> - 이 저장소에서 계속 관리하는 것: **`fieldcheck/`** (ThinQ ON 자동 점검 시스템 — 점검 장비 코드·설계 문서)
> - 아래 본문 중 웹사이트 관련 서술은 이전 완료 전 기준의 기록이므로 참고용으로만 볼 것

## 프로젝트 개요
- **공간**: 마곡 LG사이언스파크 W6동 1층, 30평형 AI홈 연구·쇼룸
- **운영 목적**: AI홈 쇼룸 지원 (B2B), 기술 연구·검증, 데이터 축적·고도화
- **호스팅**: GitHub Pages (저장소: `wonseok0415/wonseok-lab`, 하위폴더: `thinqreal/`)
- **백엔드**: Google Apps Script + Google Sheets

## 디자인 시스템
- **스타일**: Apple HIG (Human Interface Guidelines)
- **폰트**: Inter
- **그리드**: 8pt 그리드, 44pt 터치 타깃
- **메인 컬러**: `--c-accent: #3a5035` (다크 올리브 그린)

## 파일 구조
```
thinqreal/
├── thinqreal.html              # 메인 사이트 (홈/공간소개/예약/이용안내)
├── thinqreal_admin.html        # 관리자 대시보드 (8개 탭)
├── ThinQReal_AppScript.gs      # Google Apps Script (배포 완료)
├── ThinQ_Real_ROI_Tool.html    # ROI 분석 시뮬레이션 툴 (관리자 ROI 탭에서 iframe 임베드)
├── CLAUDE.md                   # 이 파일
├── fieldcheck/                 # ⚠️ 별도 시스템: ThinQ ON Field 자동 점검 (FieldCheck)
│   ├── DESIGN.md               # 설계 문서 (배경/구조/판정 3단계/이관 대비 원칙/로드맵)
│   ├── DAILY_CHECKLIST.md      # 시스템 가동 전 운영자 수동 일일 점검 체크리스트
│   ├── PROGRESS_REPORT.md      # 진행 보고서 소스 (클로드디자인 다듬기용)
│   └── rig/                    # 점검 프로그램 (노트북용 Python)
│       ├── fieldcheck.py       #   메인 — 발화·녹음·L1 판정·전송
│       ├── booking.py          #   예약 시간대 자동 회피 (시연 중 발화 방지)
│       ├── stt.py              #   L2 내용 판정 (로컬 Whisper + 키워드)
│       ├── synthesize_phrases.py  # 점검 문장 WAV 생성기
│       ├── config.example.json #   설정 예시 (config.json은 커밋 금지 — api_key 포함)
│       └── README.md           #   초보자용 설치·운영 가이드
└── images/                     # 이미지 (GitHub Raw로 참조됨)
    ├── thinqreal_*.png/jpeg    # 메인 사이트 이미지 10개
    └── thinqreal_admin_*.png   # 관리자 페이지 이미지 2개
```

## 이미지 경로 규칙
모든 이미지는 GitHub Raw URL로 참조됨:
```
https://raw.githubusercontent.com/wonseok0415/wonseok-lab/main/thinqreal/images/{파일명}
```

**중요**: 이미지를 추가하거나 수정할 때 base64로 HTML에 직접 삽입하지 말 것.
반드시 `images/` 폴더에 별도 파일로 저장하고 GitHub URL로 참조해야 함.
(과거에 base64 삽입으로 HTML이 4.3MB까지 비대해진 이슈가 있었음)

## Google Apps Script 연동
| 항목 | 값 |
|------|-----|
| Sheets ID | `1-Z158TV46MtSEArir9bW4h4KQ438NCuhb3qaGyOooA0` |
| 시트 탭명 | `bookings` (변경 금지) |
| Apps Script URL | `https://script.google.com/macros/s/AKfycbxqmzxbm99Fi9vrKgLxCslUwwEl8TxiyUN6LPMwimf04yjQjIO1s2tjC2jWKnR7iCSrSQ/exec` |
| 관리자 비밀번호 | `thinqreal2026` (3명 공유) |
| 담당자 알림 메일 수신 | 이철호(`ch275.lee@lge.com`), 서문수(`moonsu.seo@lge.com`), 김현진(`hj8462.kim@lge.com`) — 콤마 구분으로 일괄 발송 |
| CC 수신자 | `kang.wonseok@lge.com` (담당자 알림·예약자 메일 모두에 CC) |

### Apps Script 처리 엔드포인트
| 요청 | 처리 |
|------|------|
| `GET ?type=availability&date=YYYY-MM-DD` | 확정 슬롯 번호 배열 반환 |
| `GET ?type=bookings` | 전체 예약 목록 (관리자용) |
| `GET ?type=roi_snapshots` | ROI 시나리오 이력 목록 (최신순) |
| `GET ?type=mail_status` | 메일 발송 설정 + 남은 일일 할당량 (메일 미발송, 진단용) |
| `GET ?type=mail_test` | 테스트 메일 1통 발송 (실패 시 사유 응답) |
| `GET ?type=appliances` | 구비 가전 45개 목록 — `APPLIANCES` 상수의 단일 소스 |
| `POST type:booking` | Sheets 저장 + 담당자 알림 메일 |
| `POST type:update` | 상태 변경 + 예약자 확정/거절 메일 |
| `POST type:roi_snapshot` | ROI 시나리오 스냅샷 저장 (label/author/inputs/outputs) |
| `POST type:roi_delete` | ROI 시나리오 스냅샷 삭제 (id) |

### 예약자 메일 (sendGuestMail)
- **HTML + plain-text 동시 발송** — `MailApp.sendEmail({body, htmlBody})`로 두 버전을 함께 실음. HTML 클라이언트는 카드형 레이아웃, 평문 클라이언트는 평문을 받음.
- HTML은 **인라인 스타일만** 사용 (Gmail/Outlook 호환). 외부 리소스·`<style>` 블록·CSS 변수 사용 금지.
- 다크 올리브 헤더 + 라벨/값 그리드 카드형 디자인. 거절 메일도 동일 톤(헤더 색만 그레이).
- 정보 섹션 이모지 헤더: 📅 일정 / 📍 위치 / 📶 무선 인터넷(2.4G·5G 분리) / ☎ 문의(3명) / 📖 방문 안내(`GUIDE_URL`).
- **R&D 연구 목적이면** 구비 가전 표(HTML `<table>`)를 본문에 첨부 → 브라우저 폭이 좁아져도 칼럼 정렬 유지. 표 아래 안내 문구: "연구 목적의 방문에 도움이 되시도록 구비 가전 정보를 함께 안내드립니다. (R&D 연구 목적으로 예약하신 분께만 발송됩니다.)"
- 빌더: `buildConfirmText` / `buildConfirmHtml` / `buildRejectText` / `buildRejectHtml` / `buildAppliancesText` / `buildAppliancesHtml` / `escapeHtml`

### Sheets 탭 구성
- `bookings` (예약, 변경 금지)
- `roi_snapshots` (ROI 시나리오 이력) — 컬럼: `id`, `timestamp`, `label`, `author`, `inputs(JSON)`, `outputs(JSON)`
  - 시트가 없으면 Apps Script가 첫 호출 시 자동 생성

## 예약 슬롯 (확정, 변경 금지)
| 구분 | 시간 | 비고 |
|------|------|------|
| 1회차 | 09:00–10:30 | 90분 |
| 재정비 | 10:30–11:00 | |
| 점심 | 11:30–13:00 | 예약 불가 |
| 2회차 | 13:00–14:30 | 90분 |
| 재정비 | 14:30–15:00 | |
| 3회차 | 15:00–16:30 | 90분 |

## 메인 사이트 구성 (thinqreal.html)
- **홈**: AI홈 쇼룸 지원 → 기술 연구 및 검증 → 데이터 축적 및 고도화 카드 (이 순서 유지)
- **공간 소개**: 01 거실 → 02 주방 → 03 침실 → 04 런드레스룸 → 05 욕실 → 06 현관·복도
- **예약하기**: 달력 → 슬롯 다중 선택(Set 방식 토글) → 폼 → Apps Script POST
- **이용 안내**: 무선 인터넷 → 유의사항(5개 카테고리 그룹) → 기타 이용 안내 → 주차 안내 → 담당자
  - 구비 가전 테이블은 관리자 전용으로 이관됨 (R&D 연구 목적 예약 확정 메일에는 별도로 첨부)

## 관리자 대시보드 탭 (thinqreal_admin.html)
**관리 섹션**
1. 📋 예약 관리 (KPI 카드, 필터, 테이블, 승인/거절, CSV 내보내기)
2. 📊 통계
   - 방문 목적별 바 차트 — `PURPOSE_COLORS` 결정적 매핑으로 목적별 고정 색상 (R&D=올리브, B2B=오렌지, 내부 행사=퍼플, Press Tour=틸, 기타=올리브-mid). 막대 옆 컬러 도트로 시각 인식 보조.
   - 회차별 바 차트
   - 월별 방문 건수 **누적 세로 막대** — 목적별 세그먼트를 한 막대에 쌓음. 카드 상단에 색상 범례. 호버 시 `목적: N건` 툴팁.
3. 🔐 연동 계정 정보 (마스킹 없이 직접 표시, 복사 버튼)
4. 🎬 시연 시나리오 (9개 시나리오 카드)
5. 💡 조명 스위치 안내 (공간별 카드)
6. ⚙️ 시스템 구성 (조명/Homey/ThinQ/난방 카드)
7. 📦 구비 가전 (45개 품목 — 관리자 전용, Apps Script `?type=appliances`에서 fetch 후 메모리 캐시)

**분석 섹션**
8. 📈 ROI 분석 — `ThinQ_Real_ROI_Tool.html`을 iframe으로 임베드 (지연 로드, "새 창에서 열기" 버튼 제공)
   - ROI 툴 내부에 **시나리오 스냅샷 저장/불러오기** 패널 포함 (Apps Script `roi_snapshots` 탭 연동)
   - iframe 하단에 **분석 툴 동작 원리** 설명 패널: BEP / 연간가치 / N년 ROI 산식 박스, V_R&D · V_Sales(A) · V_Sales(B) · V_PR · 비용 구조 · 해석 가이드 6개 카드. 수식 폰트는 Cambria Math 17px / 15.5px (첨자 0.7em baseline 보정).

### 데이터 로딩 — Stale-while-revalidate
`loadData()`는 첫 진입 시:
1. localStorage의 마지막 응답(`thinqreal_bookings_v1`, TTL 30분)으로 **즉시 화면 렌더** — 빈 화면 시간 ≈ 0
2. 동시에 백그라운드에서 `?type=bookings` fresh fetch → 응답 도착하면 캐시 갱신 + 활성 탭 재렌더 + toast 알림

Apps Script 콜드 스타트(1~3초) 자체는 서버 측 제약이라 완전히 없앨 수 없음. 첫 방문(캐시 없음)에서 보이는 회전 스피너 + "Apps Script 콜드 스타트로 1~3초 걸릴 수 있습니다" 메시지가 정상 동작.

## 담당자
| 이름 | 직급 | 이메일 |
|------|------|--------|
| 이철호 | 책임 | ch275.lee@lge.com |
| 서문수 | 선임 | moonsu.seo@lge.com |
| 김현진 | 선임 | hj8462.kim@lge.com |

## 미완료 작업 (TODO)
- [x] **공간 소개에 욕실 추가** — `thinqreal_bathroom.jpg` 사용 (PDF p.16-17에서 추출, room-list 05번에 배치하고 현관·복도를 06번으로 이동)
- [x] **이용 안내 — 유의사항 업데이트** (PDF 슬라이드 5)
  - 카테고리별 그룹(공통/가전/공간/욕실/ThinQ)으로 재구성
  - Wi-Fi 정보: SSID `LGE_AI_HOME_2.4G` / `LGE_AI_HOME`, PW `real2026`
- [x] **이용 안내 — 기타 이용 안내 섹션 추가** (PDF 슬라이드 6)
  - 수압, 촬영, 창호, 조리, 침대, 욕실 이용 시 유의사항
- [x] **이용 안내 — 구비 가전 품목 테이블 추가** (PDF 슬라이드 7, 총 45개 품목) — 제조사 컬럼 포함
- [x] **욕실 이미지 GitHub 업로드** — `images/thinqreal_bathroom.jpg` 업로드 완료 (라이브 확인됨)
- [x] **GitHub Pages 배포** — `https://wonseok0415.github.io/wonseok-lab/thinqreal/` 정상 서빙 중
- [x] **이미지 파일명 재정리** — 해시 기반 → 의미있는 이름으로 일괄 변경 (아래 매핑 표 참조)

### 이미지 파일명 매핑 (2026-05-18 정리)
| 신규 파일명 | 용도 |
|------------|------|
| `thinqreal_home_hero.png` | 홈 페이지 메인 히어로 |
| `thinqreal_about.png` | 홈 About 섹션 (split-media) |
| `thinqreal_space_hero.jpeg` | 공간 소개 페이지 히어로 |
| `thinqreal_living_room.png` | 01 거실 |
| `thinqreal_kitchen.png` | 02 주방 |
| `thinqreal_bedroom.png` | 03 침실 |
| `thinqreal_laundress_room.png` | 04 런드레스룸 |
| `thinqreal_bathroom.jpg` | 05 욕실 |
| `thinqreal_entrance_corridor.png` | 06 현관·복도 |
| `thinqreal_guide_hero.png` | 이용 안내 페이지 히어로 |
| `thinqreal_admin_lighting.png` | 관리자 — 조명 스위치 안내 슬라이드 |
| `thinqreal_admin_system.png` | 관리자 — 시스템 구성 슬라이드 |

## FieldCheck — ThinQ ON Field 자동 점검 시스템 (설계 단계)

`fieldcheck/` 폴더는 **기존 예약 관리 웹사이트와 별도의 시스템**이다. 2026-07 ATOM TTS 서버 장애(ThinQ ON 무응답 → 시연 불가)를 계기로, ThinQ ON에게 주기적으로 말을 걸어 응답을 자동 판정·기록·알림하는 점검 장비(남는 노트북 활용)를 설계함. 상세는 `fieldcheck/DESIGN.md` 참조.

- **구축 1단계 완료 (2026-07-31 현장 검증 통과)**: `fieldcheck/rig/` (노트북용 Python 점검 프로그램 — L1 무응답 감지, 초보자 설치 가이드 포함) + Apps Script에 `health_checks` 탭·엔드포인트 (`POST type:health_check` — 점검 장비 인증 키 `FC_API_KEY`, `GET ?type=health_checks&days=N`) + 매일 아침 8시 요약 메일
- **구축 2단계 코드 완성 (2026-07-31)**: 예약 시간대 자동 회피(`rig/booking.py`) + 로컬 Whisper L2 내용 판정(`rig/stt.py`). 현장 검증 대기. 관리자 🩺 탭은 미구현(Phase 2)
- 시스템 가동 전까지는 `fieldcheck/DAILY_CHECKLIST.md`의 수동 점검으로 운영
- 사내 이관 대비 원칙(엔드포인트/인증/저장소를 설정으로 분리)은 DESIGN.md §10 — 구현 시 필수 준수

## 작업 시 주의사항
- 이미지는 절대 base64로 HTML에 삽입하지 말 것 (반드시 별도 파일 + GitHub URL)
- Apps Script URL과 Sheets ID는 절대 변경하지 말 것 (배포 완료 상태)
- 슬롯 시간표는 확정된 것이므로 변경 금지
- 디자인 시스템(Apple HIG, 다크 올리브 그린 #3a5035) 유지

## 알아두면 좋은 것
| 상황 | 재작업 필요 여부 |
|------|----------------|
| 드라이브 폴더 이동 | ✕ 불필요 (SHEET_ID 불변) |
| 시트 파일명 변경 | ✕ 불필요 |
| 탭명 "bookings" 변경 | ✓ Apps Script `SHEET_NAME` 수정 필요 |
| 시트 삭제 후 재생성 | ✓ SHEET_ID 전체 교체 필요 |
| Apps Script 재배포 | ✓ 새 URL을 두 HTML 파일에 재입력 필요 |

## 최근 작업 내역 (2026-05-17 ~ 2026-05-18)

PDF `ThinQ Real_User Guide_260507_v3.pdf`(21p, 1.87MB)의 슬라이드 5~7, 16~17을 기반으로 `thinqreal.html`을 대폭 보강함.

### 1) 공간 소개 — 욕실 추가
- 새 `room-row` 블록을 런드레스룸 다음에 삽입 (번호 05)
- 기존 현관·복도는 번호 06으로 재배치
- 이미지: `images/thinqreal_bathroom.jpg` (PDF p.16 Image82 추출, 1142×762, 57KB)
- appliance-chip: 바스에어(듀얼 배기), 스마트 수전, 온습도 센서, 재실 센서, 다운라이트, 간접조명

### 2) 유의사항 — 카테고리 그룹 재구성
- 평탄 리스트(10개) → 5개 카테고리 그룹으로 재구성
- 그룹: **공통(기본 유의사항) / 가전(가전·IoT·소품) / 공간(커튼·창호·가구·전기) / 욕실(화장실·슬리퍼) / ThinQ(계정·홈초대)**
- 새 CSS 클래스 도입: `.caution-group`, `.caution-group-header`, `.caution-cat`, `.caution-cat-sub`, 리스트 아이템에 `.note` 서브텍스트
- Wi-Fi: SSID `LGE_AI_HOME_2.4G` / `LGE_AI_HOME`, PW `real2026`

### 3) 기타 이용 안내 섹션 신설
- PDF 슬라이드 6 기반 6개 항목: 수압, 촬영, 창호, 조리, 침대, 욕실 이용
- 위치: 유의사항 다음, 구비 가전 테이블 이전

### 4) 구비 가전 테이블 확장
- 27개 → **45개 품목**으로 확장 (PDF 슬라이드 7 전체 반영)
- **제조사 컬럼 추가**
- 주요 추가: ThinQ ON(HMAK4W.AKOR), 보이스컨트롤러(HAAL3W.AKOR), AP(Unifi U7-Pro-XG), 스마트버튼×2, 도어센서, 모션조도센서, 스마트플러그, 스마트도어락, 전동창호×2, 월패드, 온도조절기, 전동커튼 등

### 핵심 제약 (다음 세션에서도 유지)
- 구비 가전 45개 순서는 PDF 슬라이드 7 그대로 유지 (재정렬 금지)
- 유의사항 카테고리 5개 그룹 구조는 PDF 기준이므로 임의 통합·분리 금지

## 작업 내역 (2026-05-19 세션)

### A. 예약 확정 메일 개편 (Apps Script — 재배포 필요)
- 평문 → **HTML + plain-text 동시 발송** 구조로 전환 (`htmlBody` + `body`)
- 카드형 레이아웃, 정보 섹션을 이모지 헤더로 정렬 (📅 📍 📶 ☎ 📖 📦)
- 무선 인터넷 **2.4 GHz / 5 GHz 분리** 표기 (PW `real2026`)
- 문의 담당자 **3명 모두** 표기 + `mailto:` 링크
- `GUIDE_URL` (이용 안내 페이지 `#page-guide` 앵커) 카드형 링크
- **R&D 연구 목적** 예약자 한정으로 구비 가전 표(HTML `<table>`) 본문 첨부 — 좁은 화면에서도 칼럼 정렬 유지
- 가전 표 아래 부드러운 안내 문구: "연구 목적의 방문에 도움이 되시도록 구비 가전 정보를 함께 안내드립니다."
- 거절 메일도 동일 톤(헤더만 그레이)으로 정렬

### B. 구비 가전 데이터 단일 소스 통합
- 메인 사이트(`thinqreal.html`)의 구비 가전 테이블 **제거** — 일반 방문자 화면에서 빠짐
- 관리자에 📦 구비 가전 탭 신설 (사이드바 "관리" 섹션)
- Apps Script에 `APPLIANCES` 상수 신설 + `GET ?type=appliances` 엔드포인트 노출
- 관리자 페이지는 첫 진입 시 엔드포인트 fetch + 메모리 캐시
- → 가전 추가·변경 시 **Apps Script 한 곳만** 수정하면 메일·관리자 동시 갱신

### C. 통계 차트 개선
- `PURPOSE_COLORS` 결정적 매핑으로 목적별 고정 색상 (위 §관리자 §2 참조)
- 막대 옆 컬러 도트(`::before` 의사 요소 + CSS 변수)
- 월별 방문 건수: 단색 → **목적별 누적 세로 막대** + 색상 범례
- `.month-bar-wrap` (영역) / `.month-bar` (실제 막대) / `.month-segment` (목적별 세그먼트) 3단 구조

### D. ROI 분석 — 동작 원리 설명 패널
- iframe 하단에 신설: BEP / 연간 창출 가치 / N년 ROI 산식 박스
- 6개 카드: 비용 구조 · V_R&D · V_Sales(A) · V_Sales(B) · V_PR · 해석 가이드
- 수식 폰트: SF Mono(12.5–14px) → **Cambria Math 17px / 15.5px**, 첨자 0.7em + baseline 보정으로 가독성 개선

### E. 초기 로딩 — Stale-while-revalidate 캐시
- localStorage 캐시(`thinqreal_bookings_v1`, TTL 30분) + 회전 스피너 UI (위 §관리자 §데이터 로딩 참조)

### 관련 PR
- #15 (8b958a8 — 메일 개편 초안 + 구비 가전 이관 + ROI 동작 원리 초안) — 머지 완료
- #16 (968eb77 + 68c1806 + 22dc358 — 단일 소스 통합 / 폰트 가독성 / 메일 HTML + 통계 색상·누적 + 캐시) — PR #15가 첫 커밋만 머지된 채 닫혀 후속 3건이 누락되어 후속 PR로 분리. 머지 후 Apps Script 재배포 필요.

## 다중 기기 작업 환경
- 이 프로젝트는 맥북 외부(iPhone/iPad/회사 PC)에서도 작업 필요
- 권장 워크플로우: 로컬 수정 → GitHub push → 다른 기기는 `claude.ai/code`(웹)에서 같은 repo 연결하여 이어서 작업
- 맥북 로컬 클론 위치: `~/workspace/wonseok-lab` (VS Code + Claude Code)

### 세션 시작/종료 리마인드 (Claude 지침 — 모든 세션 공통)
사용자가 git에 익숙해지는 중이므로, Claude는 다음을 능동적으로 챙길 것:
1. **로컬(맥북 VS Code) 세션 시작 시**: 작업 전에 `git pull` 실행 여부를 확인하고, 안 되어 있으면 대신 실행하거나 안내할 것 (다른 기기에서 푸시한 내용을 먼저 받아야 충돌 방지)
2. **작업 단위가 끝날 때마다**: 커밋 + push까지 완료했는지 확인하고, 안 했으면 리마인드할 것 (push되지 않은 로컬 커밋은 다른 기기에서 보이지 않음)
3. 웹(claude.ai/code) 세션은 자동으로 최신을 받아오므로 pull 리마인드 불필요 — push만 확인
4. **세션 마무리 시 핸드오프 기록**: 사용자가 자리를 옮기거나 세션을 마칠 때(또는 "마무리해줘"라고 하면), 그날의 진행 상황·미완료 항목을 아래 "진행 상태" 섹션에 갱신하고 커밋·푸시할 것. 채팅 히스토리는 세션 간 이동하지 않으므로 이 기록이 유일한 인수인계 수단임

## FieldCheck 진행 상태 (핸드오프 로그 — 세션 마무리 시 갱신)

**2026-08-03 — API 키 보안 조치 수용 + 예약 조회 404 복구:**
- **main 리베이스로 운영 세션의 보안 조치 유입** (thinqreal PR #51, 필독 안내는 thinqreal `CLAUDE.md` §FieldCheck): `FC_API_KEY` 하드코딩 제거 → **Script Property 조회(`getFcApiKey()`, 미설정·불일치 시 전부 거부)**. 초기 키 `fieldcheck2026`은 노출 폐기. **코드·예시·문서에 실제 키 재기록 금지**
- **rig 예약 조회 404 → 점검 스킵 발생**: 원인은 맥북 `config.json`의 `endpoint_url`이 폐기된 배포 주소를 가리킨 것. 저장소 기준 메인 배포 URL은 처음부터 `AKfycbxqmzxbm99…` 하나뿐(config.example.json 기본값 = 메인 주소) — 로컬 파일만 교정하면 됨
- 조치: `config.example.json` api_key를 자리표시자로 교체(평문 키 제거), rig README §3에 404·Unauthorized 대처 안내, DESIGN.md §9에 보안 서브섹션 신설 + **`GET ?type=health_checks` 무인증 → 관리자 토큰 게이트 검토 백로그** (운영 세션 관찰 위임분)
- **사용자 후속 (맥북 로컬)**: `config.json`의 `endpoint_url`을 메인 배포 주소로, `api_key`를 Script Property `FC_API_KEY` 새 값으로 교체 → `--once`로 확인. Apps Script는 main 최신(.gs = 보안 조치 + 07:40 스케줄)을 에디터 반영 후 **기존 배포 편집(새 버전)으로 재배포** — 새 배포를 만들면 URL이 바뀌어 모든 클라이언트가 끊김
- ⚠ 여전히 미확인: `setupFieldCheckDailyTrigger()` 1회 실행 여부 (요약 메일이 8시대에 오면 누락 신호)
- **(후속) 리포 상태 점검 (08-04)**: 맥북 config.json 교정 + `--once` 성공 확인 → 404 건 종결. 단 thinqreal에 운영 세션 PR #52·#53(월간 리포트 개편, .gs ±1,000줄)이 **머지+재배포 완료** 상태라, 세션이 보낸 `배포용_20260803.gs`는 구버전 — **에디터에 Ctrl+F로 `monthly_report_preview` 검색해 없으면 최신 main(`배포용_20260804.gs`) 재반영+재배포 필요** (8/4 팀장 리뷰·8/5 발송 전 필수) → **확인 결과 에디터 최신 (08-04 06:23, 검색 2건 일치 — 재반영 불필요, 경고 해제)**. wonseok-lab 잔여 브랜치 중 미머지 작업: `claude/gallant-faraday-G2Azk`(IoT 배치도 v10, 4커밋)·`claude/practical-davinci-70l3eh`(16커밋) — 나머지 5개는 main에 전부 반영된 빈 브랜치

**2026-08-02 — 07:30 자동 실행 첫 검증 성공 + 팀 공유 자료:**
- **07:30 정상 자동 실행 확인 (사람 개입 없음)** — 구축 1·2단계의 마지막 미검증 항목이었던 "스스로 도는가"까지 통과. 이로써 1·2단계 공식 완결
- **요약 메일 08:47 수신 — 정상 범위.** 지연 요인이 둘 겹침: ① Apps Script 시간 트리거는 8시대(08:00~09:00) 임의 시점에 실행 ② 발신이 외부 Gmail이라 사내 수신 시 **LG 보안 게이트웨이 스캔 큐**를 탐 (기존 확인 사항 — `thinqreal` 저장소 `docs/history.md` §발신자 참조. 예약 안내 메일에서 이미 겪었던 그 지연과 동일 원인)
- **응답 시간 = 처리 경로의 지문 (강원석 관찰, DESIGN.md §5 채택)**: 150ms(시간 질문)=기기 내 즉답·AI 엔진 미호출 / 2,910ms(일상 대화)=생성 엔진 / 4,620ms(날씨)=외부 서비스 연동. 이전의 "발화 종료 전 응답 시작 가능성" 가설은 이 해석으로 대체. 시나리오별 기준선이 다르므로 전체 평균이 아닌 시나리오별 추이로 볼 것. L3 확장 시 가전 단독 제어 vs 서비스 연동 제어 응답 시간 비교를 시나리오에 포함(백로그)
- **팀 공유용 진행 보고 PPT 완성** — `fieldcheck/FieldCheck_진행보고_20260802.pptx` (15장) + 생성 스크립트 `build_report_deck.js`. 내용 원본은 `PROGRESS_REPORT.md`(08-02 기준 전면 갱신) — 보고 내용 수정 시 md 먼저. 구성: 팀장 질문("시스템화 가능한가")에 대한 답을 앞에, 팀원 활용(하루 흐름·실패 대응 가이드) 중심
- 기동어 반응 구분(띵 감지)은 백로그 등록 — 구축 3단계와 함께 검토 (DESIGN.md §5)
- **(2) 점검 07:30→07:00, 요약 메일 8시대→07:40 무렵으로 앞당김** — 사내 게이트웨이 지연(08:47 수신) 때문에 시연 전 대응 여유 부족. Apps Script `FC_SUMMARY_HOUR=7` + `FC_SUMMARY_MINUTE=40`(`nearMinute`, ±15분: 07:25~07:55 — 07:00 점검 종료 후 실행 보장), 설치 스크립트 기본값 07:00, pmset 안내 06:55 (분=0일 때 시간 넘김 버그도 수정). **적용 완료 (2026-08-02 사용자 확인)**: 맥북 재설치 + pmset 06:55 + Apps Script 재배포(밀려 있던 `fcNormalizeNote()` 포함). ⚠ 트리거 교체(`setupFieldCheckDailyTrigger()` 1회 실행) 여부는 미확인 — 익일 메일이 8시대에 오면 이것이 누락된 것
- **(3) 발표자료 17장으로 확장** — L1 판정 로직(3겹 필터: 대역/기저 소음/발성 비율) + L2 Whisper 소개(팀 최초 접촉 솔루션: 로컬 실행·받아쓰기 전용·판정은 키워드 규칙) 슬라이드 추가, 운영 시각 07:00/07:40 반영

**2026-08-01 마감 — 구축 2단계 현장 검증 통과 + main 머지:**
- **첫 정상 자동 실행 성공**: `6건 판정 / 실패 0건` (L1 3건 + L2 3건 전원 통과). 기저 소음이 시나리오마다 다르게(42.6 / 50.0 / 48.5 dBA) 측정되어 마이크 정상 동작 확인
- 실측 인식 결과: `"지금은 9시 33분이에요"` / `"저는 항상 기분이 좋아요…"` / `"오늘 등천동 날씨는… 기온은 최고 34.2도…"` → 오인식이 섞였으나 **기대 키워드가 살아남아 판정은 모두 정확**
- 이번 실행에서 나온 개선 2건 반영: ① 서버 전송 타임아웃 유실 → **재시도 3회**(2·4초 간격) + 타임아웃 45초 ② STT 고유명사 오인식 → **`vocabulary_hint`**(어휘 힌트) 추가
- 용어 정리: `소음 바닥` → **`기저 소음`** (콘솔·문서 전반, 내부 필드명 `floor_dba`는 호환 위해 유지)
- **양 저장소 main 머지 완료** → Apps Script 재배포 필요 (요약 메일 L1/L2 분리 집계 반영)
- **다음**: ① 내일 07:30 자동 실행 + 08시 요약 메일 확인 ② 관리자 대시보드 🩺 탭 ③ 구축 3단계 L3(USB 웹캠 필요)
- 관찰 항목: 시간 질문의 L1 지연이 150ms로 유독 빠름(다른 건 2910·4620ms). ThinQ ON이 발화 종료 전 응답을 시작했을 가능성 — 며칠 데이터 축적 후 재검토

**2026-08-01 (3) — 요약 메일 디자인 개편 + 관리자 🩺 탭:**
- **요약 메일을 예약 확정 메일과 같은 톤의 HTML로 개편** (평문 동시 발송 유지 — HTML 미지원 클라이언트 대비)
  - 헤더 색으로 상태 표시(정상=올리브 / 실패·기록없음=레드) — 거절 메일이 헤더만 그레이로 바꾸는 기존 패턴과 동일
  - KPI 카드 3개 + 단계별 성공률 막대 + 실패 카드([L1]/[L2] 배지·인식 텍스트·⚠ 사유·녹음 파일명)
  - **'응답 시작' 측정 구간 도식 카드** — ①~⑥ 중 ⑤~⑥을 올리브로 강조. 숫자만 있고 정의가 없어 "답을 마치기까지"로 오해할 수 있었음. 평문에도 ASCII 도식 추가
- **용어 정리**: `리그` → **`점검 장비`** (팀에서 쓰지 않는 용어), `지연` → `응답 시작`. 과거 시트 기록은 `fcNormalizeNote()`로 **표시 시점에 변환**(저장값은 보존 — 이력 사후 수정 회피). 폴더명 `rig/`는 코드 경로라 유지
- **관리자 대시보드 분석 섹션에 🩺 자동 점검 탭 신설** (`thinqreal_admin.html`, 백엔드 무변경 — 기존 `?type=health_checks` 사용)
  - 오늘 상태(기록 없음 = 점검 장비 이상 신호로 표시) / L1·L2 성공률 / 평균 응답 시작 KPI
  - 일자별 성공률 — **점검이 없던 날은 빈 칸**으로 남겨 "안 돌았음"이 드러나게 함
  - 단계·시나리오별 표(scenario_id 순), 최근 실패 20건, 기간 7/14/30일 전환
  - 성공률 색 3단계(100% 올리브 / 80%+ 주황 / 미만 레드) — 100% 아니면 전부 레드는 경고가 무뎌짐
- **응답 시작(latency_ms) 정의 확정**: 점검 질문 재생이 끝난 시점(=녹음 시작)부터 ThinQ ON이 말을 시작할 때까지. 기동어 '띵' 기준 아님, 답변 총 길이 아님
- **자동 점검 탭 색상 톤다운**: 전역 `--c-red`(#ff3b30)는 예약 상태 배지용 강한 경고색이라 매일 보는 운영 지표에 부적합. `.hc-scope`에서만 차분한 팔레트 정의 — `--hc-ok #3a5035` / `--hc-warn #a8803a` / `--hc-bad #9c4a40`. 전역 변수 무변경이라 다른 탭 영향 없음. 일자별 막대에 수치 라벨 추가(점검 없는 날은 `–`로 0%와 구분)
- **맥북 자동 기상 설정 완료**: `sudo pmset repeat wakeorpoweron MTWRFSU 07:25:00` → `pmset -g sched`로 확인됨. 이로써 자동 실행 3요소(launchd 등록 / 마이크 권한 / 자동 기상) 모두 충족. **완전 종료 금지** — 전원이 꺼진 상태에서 켜지면 로그인 화면에 멈춰 LaunchAgent가 실행되지 않음. 덮개만 닫고 전원 연결 유지

**2026-08-01 (4) — 구축 3단계(L3) 판정 방식 확정 (착수 전 설계):**
- **AI 영상 인식 미사용 확정** — 카메라·쇼룸 배치가 고정이라 "이게 뭔지 인식"이 아니라 "아까와 달라졌나 비교" 문제. 관심영역(ROI) 픽셀 비교(산술 연산)로 충분. L2에서 Whisper가 필요했던 것과 성격이 다름
- 대상별 지표: 조명=평균 밝기 / 커튼=변화 픽셀 비율 + 경계선 이동 / 무드등=Hue 히스토그램 / TV=밝기+프레임 변동. **에어컨 설정온도(숫자 판독)는 AI·OCR 영역이라 초기 범위 제외**
- **웹캠 자동 노출 함정 — 마이크 권한 함정과 같은 급의 조용한 실패**: 조명을 켜면 카메라가 스스로 노출을 낮춰 평균 밝기가 그대로 → 정상 동작을 "변화 없음=실패"로 오판정. 대응 ① 노출·게인·WB 수동 고정(macOS는 제한적, **Windows 전환의 추가 근거**) ② 고정 불가 시 "안 변하는 벽" 참조 영역과의 **상대 비교**
- 촬영은 단발이 아닌 **연속 촬영**(발화 후 25초간 1초 간격) 후 변화 구간 검출 — 조명은 즉시지만 커튼은 10~20초라 단발은 타이밍이 빗나감. 덤으로 "명령 후 몇 초 만에 움직였는가" 확보
- **카메라 자기진단 필수** — 미연결·렌즈 가림이면 전/후가 같아 가전 장애로 오보. L1 무음 감지와 같은 구조로 `점검 장비 문제` 분류
- **ThinQ API 상태 조회보다 카메라 우선** (사용자 동의) — API는 "명령 접수"만 확인하고, 명령은 받았으나 모터가 안 도는 경우를 못 잡음. 방문객 눈에 보이는 것은 물리 변화
- 준비물: USB 웹캠 1대 + **삼각대**(고정이 정확도를 좌우) + 가전 제어 WAV. 착수 순서: 조명 1건 → 커튼
- 상세는 `fieldcheck/DESIGN.md` §5. **착수 여부는 07:30 자동 실행 검증 후 결정**

**2026-08-01 — 자동 실행 추가 (점검 장비가 안 돌던 문제):**
- 아침 요약 메일이 **"⚠ 점검 기록 없음"**으로 발송됨 → 판정 로직 문제가 아니라 **점검 장비가 그날 한 번도 실행되지 않은 것**. 수동 `--once`에만 의존하고 있었고, 맥북이 정해진 시각에 스스로 실행하는 장치가 없었음
- `rig/schedule/` 추가 — **매일 07:30 자동 실행** (1회차 09:00 회피 구간 08:40보다 앞서 충돌 없음, 08시 요약 메일에 당일 결과 포함)
  - 맥: `install_macos.sh` (launchd LaunchAgent) + `sudo pmset repeat wakeorpoweron`으로 자동 기상. **설치 후 `launchctl kickstart`로 한 번 수동 실행해 마이크 권한을 승인해야 함** (백그라운드 첫 실행에서 권한 창을 놓치면 조용히 실패)
  - Windows(상주 장비): `install_windows.ps1` (작업 스케줄러, WakeToRun + StartWhenAvailable). 스피커·마이크 사용 때문에 로그온 세션 필요
- `--upgrade-config` 추가 — config.json에 **새로 생긴 항목만** 채우고 기존 값(보정값 87.4 등)은 보존. 버전 업 때마다 손으로 고치다 빠뜨리는 문제 해소. `.bak` 백업 생성, 두 번 실행해도 안전
- 교훈: **판정이 정확해도 실행되지 않으면 무의미** — 자동 실행은 선택이 아니라 필수 구성요소 (DESIGN.md §8 기록)
- **macOS 마이크 권한 함정 (같은 날 후속)**: 자동 실행 첫 점검이 3건 모두 FAIL. 원인은 ThinQ ON이 아니라 **launchd가 실행한 python3에 마이크 권한이 없던 것**. macOS는 앱 번들이 아닌 실행 파일에는 권한 창을 띄우지 않고 **오류 없이 무음을 반환**하며, 시스템 설정 마이크 목록에도 안 나타나 수동 허용도 불가
  - 판별 단서: 세 시나리오의 dBA 값이 소수점까지 동일(2.4 / -32.6)하고 최고가 바닥보다 낮음 → 보정값 87.4를 빼면 -120.0dB(에너지 0)
  - 대응 ①: launchd가 `open -a Terminal <run_once.command>`로 실행하도록 변경 — 터미널은 정식 앱이라 권한 창이 정상 표시됨
  - 대응 ②: 무음 자동 감지 → 콘솔 경고 + 시트 `note`에 "점검 장비 설정/권한 문제(ThinQ ON 장애 아님)" 기록 + `--mic-test` 진단 명령 추가
  - Windows 상주 장비로 옮기면 이 제약은 자연 해소됨

**2026-07-31 (2) — 구축 2단계 코드 완성:**
- **1단계 마감 확인**: 첫 자동 08시 요약 메일 정상 수신(강원석 단독 수신 확인). 실패 3건은 모두 재배포 이전(06:51~06:52) 기록이며 이후 6건은 전원 성공
- **구축 2단계 구현 완료** (현장 검증은 대기):
  - `rig/booking.py` — 발화 전 `?type=availability` 조회 → 확정 예약 + 관리자 차단 슬롯 시간대(시작 20분 전 ~ 종료 10분 후)에는 점검 스킵. 조회 실패 시 당일 캐시 재사용, 캐시도 없으면 **건너뜀**(시연 방해 방지 우선). `--force`로 강행 가능
  - `rig/stt.py` — **로컬 Whisper**(faster-whisper 우선, openai-whisper 폴백)로 L2 내용 판정. 클라우드 STT 안은 철회(보안 검토 회피·오프라인 판정·과금 없음). 엔진 미설치 시 L2만 건너뛰고 L1은 그대로 동작
  - L2는 **L1 통과 건에만** 판정 → L2 성공률 = "응답한 것 중 내용까지 맞은 비율"
  - `--transcribe` 추가 — 저장된 녹음으로 발화 없이 키워드 튜닝
  - selftest 18건(기존 7 + L2 5 + 슬롯 6) 전원 통과
- **Apps Script**(`thinqreal` 저장소, 브랜치 `claude/fieldcheck-stage2-summary`): 요약 메일을 **판정 단계(L1/L2)별로 나눠 집계** + L2 실패 시 STT 인식 텍스트 표시. 스텁 실행으로 본문 확인 완료
- **다음 할 일**: ① 맥북에서 `pip3 install faster-whisper` → `--selftest` → `--transcribe`로 기존 녹음 키워드 튜닝 → `--once` 현장 검증 ② `config.json`에 `booking_avoidance`/`stt` 블록 추가(예시는 `config.example.json`) ③ `thinqreal` 브랜치 머지 후 Apps Script 재배포 ④ 검증 통과 시 양 저장소 main 머지
- **미검증 항목(샌드박스 제약)**: 실제 예약 조회 GET, Whisper 모델 로딩·인식 — 둘 다 이 환경에서 아웃바운드가 차단되어 맥북 확인 필요

**2026-07-31 마감:**
- **구축 1단계 main 머지 완료** — wonseok-lab 작업 브랜치 + thinqreal의 claude/fieldcheck-health-endpoint 모두 main 반영
- 이후 확인 사항: ① 익일 아침 자동 요약 메일(✅ 기대) ② 시각 표시 수정분(64119cb)이 포함된 main 기준으로 다음 재배포 시 자동 해소
- 다음 작업: 구축 2단계 — 예약 슬롯 자동 회피 + 로컬 Whisper L2 내용 판정

**2026-07-31 갱신:**
- **구축 1단계 현장 검증 통과** — 적응형(dBA·발성 비율) 판정으로 소음 환경(에어컨·선풍기)에서 실패 0건
- 서버 파이프라인 완성: 재배포 완료, Sheets `health_checks` 기록, 일일 아침 요약 메일 수신 확인 (테스트 모드 — 강원석에게만, 텔레그램 미발송, 건별 알림 끔)
- dBA 실측 보정 완료: `dba_calibration_offset 87.4` (휴대폰 소음앱 42dBA 대비 1점 교정, 42 근처 확인). 점검 장비 config 확정: wake_gap 1.5s, voice_over_floor_db 8
- **남은 마감**: ① 다음 아침 "✅ 전체 정상" 요약 메일 확인 ② 확인 후 양 저장소 브랜치 main 머지(wonseok-lab 작업 브랜치 + thinqreal의 claude/fieldcheck-health-endpoint — 시각 표시 수정분 재배포 포함) ③ 1단계 공식 마감 후 구축 2단계(예약 슬롯 회피 + 로컬 Whisper L2) 착수

**2026-07-30 기준:**
- 구축 1단계 코드 완성, 맥북에서 현장 테스트 진행 중 (실제 ThinQ ON 응답 확인됨)
- 현장 발견 반영 완료: 기동어 후 '띵' 대기(1.2s) / 연산 대기음 오판 방지(발성 비율 판정) / 시나리오 간 무조건 조용해질 때까지 대기 / 스몰톡 문장을 즉답형("오늘 기분 어때?")으로 교체
- **중대 사고 예방 (2026-07-30)**: 실서비스 Apps Script 소스가 `wonseok0415/thinqreal` 저장소로 이전 완료된 상태였음이 확인됨. 이 저장소의 구버전 .gs에 작업했던 health_check 추가분을 실서비스 저장소의 **`claude/fieldcheck-health-endpoint` 브랜치**로 이식 완료 (순수 추가, 텔레그램 알림 포함). 구버전 .gs는 경고 안내문으로 교체
- **미완료**: ① 실서비스 저장소에서 위 브랜치 확인·머지 후 그 파일로 Apps Script 재배포 ② 맥북에서 config 재복사 + smalltalk.wav 재생성 + --calibrate + --once 재검증 ③ 인식 성공률 반복 확인 후 음성 파일 확정
- 배포 URL은 이전 전과 동일 (rig config 기본값 유효)
- 다음 큰 단계: 구축 2단계 (STT 내용 판정 L2 + 예약 슬롯 회피)
- 새 세션은 이 `CLAUDE.md`를 자동 로드 → 프로젝트 맥락은 유지되나, **개별 채팅 히스토리는 세션 간 이동되지 않음**
- 중요한 결정/변경은 이 파일에 즉시 기록할 것

### 구형 iPad + 셀룰러에서 Claude Code 웹을 쓸 때
사용자 환경: 구형 iPad(Claude 앱 미지원) + 회사 셀룰러 데이터.

**증상**: 타이머는 흘러가는데 응답 내용이 비어 있다가, 브라우저 새로고침을 하면 그동안의 출력이 한꺼번에 나타남.

**원인 요지**: 이통사 미들박스의 유휴 연결 타임아웃 + 구형 Safari의 SSE/스트림 처리 한계로, 서버 측 출력은 계속 진행되지만 클라이언트로의 통로가 조용히 끊김. 새로고침으로 재접속하면 서버에 버퍼된 결과를 다시 받아오는 패턴.

**대응(효과 순)**:
1. **Wi-Fi 우선 사용** — 캐리어 미들박스 자체를 우회
2. iOS 설정 → 셀룰러 → "데이터 절약 모드(Low Data Mode)" 끄기
3. Claude Code 탭을 **포그라운드로 유지** (다른 앱 전환·잠금 금지)
4. VPN (Cloudflare WARP 등) — 미들박스 우회 효과
5. **새로고침을 정상 도구로 활용** — 세션은 서버에 보존되므로 진행 상황이 사라지지 않음. 응답이 오래 멈췄다 싶으면 새로고침하여 재접속
6. 긴 작업은 **GitHub Actions** 트리거로 비동기 실행 (https://code.claude.com/docs/en/claude-code-on-the-web)

## 진행 중 (2026-05-19 시점) — 도메인 이전 작업

ThinQ Real을 독립 도메인 `thinqreal.com` (hosting.kr에서 구입)으로 이전하는 작업이 진행 중. 새 세션에서 이 항목부터 확인할 것.

### 결정된 사항
- **도메인**: `thinqreal.com` (hosting.kr 구입)
- **신규 리포**: `wonseok0415/thinqreal` (별도 분리, 루트 = 사이트 루트)
- **이전 사유**: 현재 `wonseok-lab/thinqreal/` 하위 경로 구조는 도메인 연결 시 `thinqreal.com/thinqreal/thinqreal.html`처럼 지저분해짐 → 리포 분리로 `thinqreal.com/`만으로 접속 가능하게.

### 단계별 체크리스트
1. [ ] hosting.kr에서 `thinqreal.com` 구매 (WHOIS 보호 / 자동 갱신 ON 권장)
2. [ ] GitHub에서 `wonseok0415/thinqreal` 신규 리포 생성 (Public, README 포함)
3. [ ] Claude App에 신규 리포 접근 권한 부여 (github.com/settings/installations → Claude → Configure)
4. [ ] Claude Code 웹에서 **신규 리포로 새 세션 시작**
5. [ ] `wonseok-lab/thinqreal/` 폴더 전체를 신규 리포 루트로 이전
   - `thinqreal.html`, `thinqreal_admin.html`, `ThinQReal_AppScript.gs`, `ThinQ_Real_ROI_Tool.html`, `CLAUDE.md`, `images/` 통째로
   - **이미지 경로 변환**: 현재 코드에 박힌 `https://raw.githubusercontent.com/wonseok0415/wonseok-lab/main/thinqreal/images/...` 절대 URL을 상대경로 `./images/...` (또는 `images/...`)로 일괄 교체
     - 대표 위치: `thinqreal.html` 네비바 로고 (`LG_AI_Home_logo.png`), 본문 이미지들
     - `thinqreal_admin.html`도 동일 검토
   - 본 `CLAUDE.md`의 "이미지 경로 규칙" 섹션도 신규 리포 기준으로 갱신
6. [ ] 신규 리포 Settings → Pages → Source: main / (root) 선택 → 임시 주소(`wonseok0415.github.io/thinqreal/`)로 동작 확인
7. [ ] hosting.kr DNS 레코드 추가:
   ```
   A    @    185.199.108.153
   A    @    185.199.109.153
   A    @    185.199.110.153
   A    @    185.199.111.153
   CNAME www  wonseok0415.github.io
   ```
8. [ ] 신규 리포 Settings → Pages → Custom domain: `thinqreal.com` → Save (자동 `CNAME` 파일 생성)
9. [ ] DNS 전파 후 Enforce HTTPS 체크
10. [ ] **Apps Script `GUIDE_URL` 교체**: `https://wonseok0415.github.io/wonseok-lab/thinqreal/thinqreal.html#page-guide` → `https://thinqreal.com/#page-guide` → **Apps Script 재배포**
11. [ ] 옛 경로(`wonseok-lab/thinqreal/`) 처리 방침 결정:
    - 옵션 A: 그대로 유지 (옛 북마크 유저 대비)
    - 옵션 B: 폴더 삭제 + README에 새 도메인 안내만 남기기
    - 옵션 C: `thinqreal.html`을 새 도메인으로 자동 리다이렉트하는 stub만 남기기
12. [ ] CLAUDE.md에서 본 "진행 중" 섹션을 "완료 내역"으로 이동 + 호스팅 정보 표(프로젝트 개요 / Apps Script URL 등) 신규 도메인 기준으로 갱신

### 주의사항
- Apps Script URL, Sheets ID, 슬롯 시간표, 디자인 시스템은 **불변** (기존 §작업 시 주의사항 참조)
- 이전 후에도 Apps Script 자체는 그대로 사용 (URL 변경 없음). `GUIDE_URL`만 교체 + 재배포 1회 필요.
- 신규 리포로 옮긴 직후 **이미지가 깨져 보이면** 절대 URL 잔존 흔적이므로 grep으로 `raw.githubusercontent.com/wonseok0415/wonseok-lab` 검색해 모두 상대경로로 교체할 것.
