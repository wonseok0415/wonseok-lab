# ThinQ Real 운영관리 웹사이트

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
├── thinqreal_admin.html        # 관리자 대시보드 (6개 탭)
├── ThinQReal_AppScript.gs      # Google Apps Script (배포 완료)
├── CLAUDE.md                   # 이 파일
└── images/                     # 이미지 (GitHub Raw로 참조됨)
│   ├── thinqreal_*.png/jpeg   # 메인 사이트 이미지 10개
│   └── thinqreal_admin_*.png  # 관리자 페이지 이미지 2개
└── ThinQ_Real_ROI_Tool.html   # ROI 분석 시뮬레이션 툴 (관리자 → 분석 → ROI 분석 탭에서 iframe으로 임베드)
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

### 예약자 메일 (sendGuestMail)
- **HTML + plain-text 동시 발송** — `MailApp.sendEmail({body, htmlBody})`
- HTML은 인라인 스타일만 사용 (Gmail/아웃룩 호환)
- R&D 연구 목적이면 구비 가전 표(HTML `<table>`)를 본문에 첨부 → 브라우저 폭 변화에도 정렬 유지
- 확정 메일 카드형 레이아웃 (다크 올리브 헤더 + 라벨/값 그리드)
- 거절 메일도 동일 디자인으로 정렬
| `POST type:booking` | Sheets 저장 + 담당자 알림 메일 |
| `POST type:update` | 상태 변경 + 예약자 확정/거절 메일 |
| `POST type:roi_snapshot` | ROI 시나리오 스냅샷 저장 (label/author/inputs/outputs) |
| `POST type:roi_delete` | ROI 시나리오 스냅샷 삭제 (id) |

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
2. 📊 통계 (목적별/회차별/월별 바 차트)
3. 🔐 연동 계정 정보 (마스킹 없이 직접 표시, 복사 버튼)
4. 🎬 시연 시나리오 (9개 시나리오 카드)
5. 💡 조명 스위치 안내 (공간별 카드)
6. ⚙️ 시스템 구성 (조명/Homey/ThinQ/난방 카드)
7. 📦 구비 가전 (45개 품목 — 관리자 전용, Apps Script `?type=appliances`에서 fetch)

**분석 섹션**
8. 📈 ROI 분석 — `ThinQ_Real_ROI_Tool.html`을 iframe으로 임베드 (지연 로드, "새 창에서 열기" 버튼 제공)
   - ROI 툴 내부에 **시나리오 스냅샷 저장/불러오기** 패널 포함 (Apps Script `roi_snapshots` 탭 연동)
   - iframe 하단에 **분석 툴 동작 원리** 설명 패널: BEP/연간가치/ROI 산식, V_R&D·V_Sales·V_PR 카드별 정의, 해석 가이드

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
| `thinqreal_floor_plan.jpeg` | 공간 구성도 (도면) |
| `thinqreal_living_room.png` | 01 거실 |
| `thinqreal_kitchen.png` | 02 주방 |
| `thinqreal_bedroom.png` | 03 침실 |
| `thinqreal_laundress_room.png` | 04 런드레스룸 |
| `thinqreal_bathroom.jpg` | 05 욕실 |
| `thinqreal_entrance_corridor.png` | 06 현관·복도 |
| `thinqreal_guide_hero.png` | 이용 안내 페이지 히어로 |
| `thinqreal_admin_lighting.png` | 관리자 — 조명 스위치 안내 슬라이드 |
| `thinqreal_admin_system.png` | 관리자 — 시스템 구성 슬라이드 |

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

## 다중 기기 작업 환경
- 이 프로젝트는 맥북 외부(iPhone/iPad/회사 PC)에서도 작업 필요
- 권장 워크플로우: 로컬 수정 → GitHub push → 다른 기기는 `claude.ai/code`(웹)에서 같은 repo 연결하여 이어서 작업
- 새 세션은 이 `CLAUDE.md`를 자동 로드 → 프로젝트 맥락은 유지되나, **개별 채팅 히스토리는 세션 간 이동되지 않음**
- 중요한 결정/변경은 이 파일에 즉시 기록할 것
