# ThinQ Real 운영관리 웹사이트

## 프로젝트 개요
- **공간**: 마곡 LG사이언스파크 W6동 1층, 30평형 AI홈 연구·쇼룸
- **운영 목적**: AI홈 쇼룸 지원 (B2B), 기술 연구·검증, 데이터 축적·고도화
- **호스팅**: GitHub Pages (저장소: `wonseok-lab/wonseok-lab`, 하위폴더: `thinqreal/`)
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
    ├── thinqreal_*.png/jpeg   # 메인 사이트 이미지 10개
    └── thinqreal_admin_*.png  # 관리자 페이지 이미지 2개
```

## 이미지 경로 규칙
모든 이미지는 GitHub Raw URL로 참조됨:
```
https://raw.githubusercontent.com/wonseok-lab/wonseok-lab/main/thinqreal/images/{파일명}
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
| 관리자 비밀번호 | `thinqreal2026` |

### Apps Script 처리 엔드포인트
| 요청 | 처리 |
|------|------|
| `GET ?type=availability&date=YYYY-MM-DD` | 확정 슬롯 번호 배열 반환 |
| `GET ?type=bookings` | 전체 예약 목록 (관리자용) |
| `POST type:booking` | Sheets 저장 + 담당자 알림 메일 |
| `POST type:update` | 상태 변경 + 예약자 확정/거절 메일 |

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
- **공간 소개**: 거실, 주방, 침실, 런드레스룸, 현관·복도 (욕실 추가 예정)
- **예약하기**: 달력 → 슬롯 다중 선택(Set 방식 토글) → 폼 → Apps Script POST
- **이용 안내**: 무선 인터넷, 유의사항, 주차 안내, 담당자

## 관리자 대시보드 탭 (thinqreal_admin.html)
1. 📋 예약 관리 (KPI 카드, 필터, 테이블, 승인/거절, CSV 내보내기)
2. 📊 통계 (목적별/회차별/월별 바 차트)
3. 🔐 연동 계정 정보 (마스킹 없이 직접 표시, 복사 버튼)
4. 🎬 시연 시나리오 (9개 시나리오 카드)
5. 💡 조명 스위치 안내 (공간별 카드)
6. ⚙️ 시스템 구성 (조명/Homey/ThinQ/난방 카드)

## 담당자
| 이름 | 직급 | 이메일 |
|------|------|--------|
| 이철호 | 책임 | ch275.lee@lge.com |
| 서문수 | 선임 | moonsu.seo@lge.com |
| 김현진 | 선임 | hj8462.kim@lge.com |

## 미완료 작업 (TODO)
- [ ] **공간 소개에 욕실 추가** (User Guide PDF p.16-17 이미지 사용)
- [ ] **이용 안내 — 유의사항 업데이트** (PDF 슬라이드 5)
  - Wi-Fi 정보: SSID `LGE_AI_HOME_2.4G` / `LGE_AI_HOME`, PW `real2026`
- [ ] **이용 안내 — 기타 이용 안내 섹션 추가** (PDF 슬라이드 6)
  - 수압, 촬영, 창호, 조리, 침대, 욕실 이용 시 유의사항
- [ ] **이용 안내 — 구비 가전 품목 테이블 추가** (PDF 슬라이드 7, 총 45개 품목)
- [ ] **이미지 파일명 재정리** (현재 해시 기반 → 의미있는 이름으로)
  - 예: `thinqreal_0b405e71.png` → `living_room_1.png`
- [ ] **GitHub Pages 배포**

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
