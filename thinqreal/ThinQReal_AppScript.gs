// ============================================================
//  ThinQ Real — Google Apps Script
//  역할: 예약 저장 / 가용성 조회 / 승인·거절 처리 + 메일 발송
//
//  배포 방법:
//  1. script.google.com → 새 프로젝트 생성
//  2. 이 코드 전체 붙여넣기
//  3. SHEET_ID를 실제 Google Sheets ID로 교체
//  4. 배포 → 새 배포 → 웹 앱 → 액세스: 모든 사용자 → 배포
//  5. 생성된 URL을 thinqreal.html과 thinqreal_admin.html의
//     SCRIPT_URL 변수에 붙여넣기
// ============================================================

// ── 설정값 ──────────────────────────────────────────────────
const SHEET_ID   = '1-Z158TV46MtSEArir9bW4h4KQ438NCuhb3qaGyOooA0';  // ← Sheets URL의 /d/ 뒤 ID
const SHEET_NAME = 'bookings';               // 시트 탭 이름 (예약)
const ROI_SHEET_NAME = 'roi_snapshots';      // 시트 탭 이름 (ROI 시나리오 이력)
// 신규 예약 알림을 받는 담당자들 (콤마로 구분, MailApp이 다중 수신 처리)
const ADMIN_EMAILS = 'ch275.lee@lge.com, moonsu.seo@lge.com, hj8462.kim@lge.com';
const CC_EMAIL     = 'kang.wonseok@lge.com';  // 참조 수신자 (시스템 동작 모니터링)


// ============================================================
//  GET 요청 처리
//  - ?type=bookings       → 전체 예약 목록 반환 (관리자용)
//  - ?type=availability&date=YYYY-MM-DD → 해당 날짜 마감 슬롯 반환
// ============================================================
function doGet(e) {
  const type = e.parameter.type;

  if (type === 'availability') {
    return handleAvailability(e.parameter.date);
  }
  if (type === 'bookings') {
    return handleGetBookings();
  }
  if (type === 'roi_snapshots') {
    return handleGetRoiSnapshots();
  }

  return jsonResponse({ error: 'Unknown type' });
}


// ── 가용성 조회 ─────────────────────────────────────────────
// 확정(status = '확정') 된 예약만 마감으로 처리
// 대기중은 마감으로 처리하지 않음 (담당자가 거절할 수 있으므로)
function handleAvailability(date) {
  if (!date) return jsonResponse({ bookedSlots: [] });

  const sheet = getSheet();
  const rows  = sheet.getDataRange().getValues();
  const headers = rows[0];
  const dateIdx   = headers.indexOf('date');
  const slotIdx   = headers.indexOf('slots');   // 복수 슬롯 (JSON 배열)
  const statusIdx = headers.indexOf('status');

  const booked = new Set();

  for (let i = 1; i < rows.length; i++) {
    const row = rows[i];
    if (row[dateIdx] !== date) continue;
    if (row[statusIdx] !== '확정') continue;

    // slots 컬럼은 "[1,2]" 형태의 JSON 문자열로 저장됨
    try {
      const slots = JSON.parse(row[slotIdx]);
      slots.forEach(s => booked.add(Number(s)));
    } catch(err) {
      // 구형 데이터(slot 단일값) 대응
      const singleSlot = headers.indexOf('slot');
      if (singleSlot >= 0 && row[singleSlot]) {
        booked.add(Number(row[singleSlot]));
      }
    }
  }

  return jsonResponse({ bookedSlots: [...booked] });
}


// ── 전체 예약 목록 조회 (관리자) ────────────────────────────
function handleGetBookings() {
  const sheet   = getSheet();
  const rows    = sheet.getDataRange().getValues();
  const headers = rows[0];

  const records = rows.slice(1).map((row, i) => {
    const obj = { id: String(i + 1) };
    headers.forEach((h, j) => { obj[h] = row[j] ?? ''; });
    // id 컬럼이 없으면 행 인덱스로 부여
    if (!obj.id || obj.id === '') obj.id = String(i + 1);
    return obj;
  }).filter(r => r.date); // 빈 행 제외

  return jsonResponse({ records });
}


// ============================================================
//  POST 요청 처리
//  - type: 'booking' → 신규 예약 저장 + 담당자 알림 메일
//  - type: 'update'  → 상태 변경 + 예약자 확정/거절 메일
// ============================================================
function doPost(e) {
  let data;
  try {
    data = JSON.parse(e.postData.contents);
  } catch(err) {
    return jsonResponse({ error: 'Invalid JSON' });
  }

  if (data.type === 'booking') return handleNewBooking(data);
  if (data.type === 'update')  return handleUpdateStatus(data);
  if (data.type === 'roi_snapshot') return handleNewRoiSnapshot(data);
  if (data.type === 'roi_delete')   return handleDeleteRoiSnapshot(data);

  return jsonResponse({ error: 'Unknown type' });
}


// ── 신규 예약 저장 ───────────────────────────────────────────
function handleNewBooking(data) {
  const sheet   = getSheet();
  const headers = getOrCreateHeaders(sheet);

  // 고유 ID 생성 (타임스탬프 기반)
  const id = String(Date.now());

  const row = headers.map(h => {
    if (h === 'id')        return id;
    if (h === 'slots')     return JSON.stringify(data.slots || [data.slot]);
    if (h === 'timestamp') return data.timestamp || new Date().toISOString();
    return data[h] ?? '';
  });

  sheet.appendRow(row);

  // 담당자 알림 메일
  sendAdminAlert(data, id);

  return jsonResponse({ success: true, id });
}


// ── 상태 업데이트 (확정 / 거절) ─────────────────────────────
function handleUpdateStatus(data) {
  const sheet   = getSheet();
  const rows    = sheet.getDataRange().getValues();
  const headers = rows[0];
  const idIdx     = headers.indexOf('id');
  const statusIdx = headers.indexOf('status');

  let targetRow = -1;
  for (let i = 1; i < rows.length; i++) {
    if (String(rows[i][idIdx]) === String(data.id)) {
      targetRow = i + 1; // Sheets는 1-based
      break;
    }
  }

  if (targetRow < 0) return jsonResponse({ error: 'Record not found' });

  // status 컬럼 값 변경
  sheet.getRange(targetRow, statusIdx + 1).setValue(data.status);

  // 예약자에게 확정/거절 메일 발송
  if (data.email) sendGuestMail(data);

  return jsonResponse({ success: true });
}


// ============================================================
//  메일 발송
// ============================================================

// 담당자 알림 메일 (신규 예약 접수 시)
function sendAdminAlert(data, id) {
  const slotLabel = data.slotLabel || '';
  const subject   = `[ThinQ Real] 새 예약 신청 — ${data.date} ${slotLabel}`;
  const body = `
새로운 예약 신청이 접수되었습니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  예약 ID : ${id}
  날  짜  : ${data.date}
  회  차  : ${slotLabel}
  이  름  : ${data.name}
  소  속  : ${data.org}
  연락처  : ${data.phone}
  이메일  : ${data.email}
  목  적  : ${data.purpose}
  인  원  : ${data.count}명
  요청사항: ${data.note || '없음'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

관리자 페이지에서 승인 또는 거절해 주세요.
  `.trim();

  try {
    MailApp.sendEmail({ to: ADMIN_EMAILS, cc: CC_EMAIL, subject, body });
  } catch(err) {
    Logger.log('Admin mail error: ' + err.message);
  }
}

// 예약자 확정/거절 메일
function sendGuestMail(data) {
  const isConfirmed = data.status === '확정';
  const subject = isConfirmed
    ? `[ThinQ Real] 예약이 확정되었습니다 — ${data.date} ${data.slotLabel || ''}`
    : `[ThinQ Real] 예약 신청이 거절되었습니다`;

  const body = isConfirmed ? `
안녕하세요, ${data.name}님.

ThinQ Real 방문 예약이 확정되었습니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  날  짜 : ${data.date}
  회  차 : ${data.slotLabel || ''}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 위치: 마곡 LG사이언스파크 W6동 1층
   보안게이트 출구 앞 / 주차장 엘리베이터 앞
   (보안게이트 밖에 위치해 별도 보안 절차 없이 방문 가능합니다.)

📶 Wi-Fi: LGE_AI_HOME_2.4G / LGE_AI_HOME  (PW: real2026)

방문 전 이용 안내를 확인해 주세요:
https://[배포된 URL]/thinqreal.html

문의: ch275.lee@lge.com

감사합니다.
HS플랫폼사업센터 AI홈솔루션엔지니어링팀
  `.trim() : `
안녕하세요, ${data.name}님.

아쉽게도 요청하신 일정에 ThinQ Real 예약이 어렵게 되었습니다.

다른 일정으로 다시 신청해 주시거나, 아래 담당자에게 문의해 주세요.

  이철호 책임 연구원: ch275.lee@lge.com
  서문수 선임 연구원: moonsu.seo@lge.com
  김현진 선임 연구원: hj8462.kim@lge.com

감사합니다.
HS플랫폼사업센터 AI홈솔루션엔지니어링팀
  `.trim();

  try {
    MailApp.sendEmail({ to: data.email, cc: CC_EMAIL, subject, body });
  } catch(err) {
    Logger.log('Guest mail error: ' + err.message);
  }
}


// ============================================================
//  헬퍼 함수
// ============================================================

function getSheet() {
  return SpreadsheetApp
    .openById(SHEET_ID)
    .getSheetByName(SHEET_NAME)
    || SpreadsheetApp.openById(SHEET_ID).insertSheet(SHEET_NAME);
}

// ============================================================
//  ROI 시나리오 스냅샷 (이력 관리)
//  - 시트 탭: roi_snapshots
//  - 컬럼: id, timestamp, label, author, inputs(JSON), outputs(JSON)
// ============================================================

function getRoiSheet() {
  const ss = SpreadsheetApp.openById(SHEET_ID);
  return ss.getSheetByName(ROI_SHEET_NAME) || ss.insertSheet(ROI_SHEET_NAME);
}

function getOrCreateRoiHeaders(sheet) {
  const HEADERS = ['id', 'timestamp', 'label', 'author', 'inputs', 'outputs'];
  const firstRow = sheet.getRange(1, 1, 1, HEADERS.length).getValues()[0];
  if (!firstRow[0]) {
    sheet.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]);
    const headerRange = sheet.getRange(1, 1, 1, HEADERS.length);
    headerRange.setBackground('#3a5035');
    headerRange.setFontColor('#ffffff');
    headerRange.setFontWeight('bold');
    sheet.setFrozenRows(1);
  }
  return HEADERS;
}

function handleGetRoiSnapshots() {
  const sheet = getRoiSheet();
  getOrCreateRoiHeaders(sheet);
  const rows = sheet.getDataRange().getValues();
  const headers = rows[0];
  const records = rows.slice(1).map(row => {
    const obj = {};
    headers.forEach((h, j) => { obj[h] = row[j] ?? ''; });
    try { obj.inputs  = JSON.parse(obj.inputs  || '{}'); } catch(err) { obj.inputs  = {}; }
    try { obj.outputs = JSON.parse(obj.outputs || '{}'); } catch(err) { obj.outputs = {}; }
    return obj;
  }).filter(r => r.id);
  // 최신순 정렬 (timestamp 내림차순)
  records.sort((a, b) => String(b.timestamp).localeCompare(String(a.timestamp)));
  return jsonResponse({ records });
}

function handleNewRoiSnapshot(data) {
  const sheet = getRoiSheet();
  const headers = getOrCreateRoiHeaders(sheet);
  const id = String(Date.now());
  const row = headers.map(h => {
    if (h === 'id')        return id;
    if (h === 'timestamp') return data.timestamp || new Date().toISOString();
    if (h === 'inputs')    return JSON.stringify(data.inputs  || {});
    if (h === 'outputs')   return JSON.stringify(data.outputs || {});
    return data[h] ?? '';
  });
  sheet.appendRow(row);
  return jsonResponse({ success: true, id });
}

function handleDeleteRoiSnapshot(data) {
  const sheet = getRoiSheet();
  const rows = sheet.getDataRange().getValues();
  const headers = rows[0];
  const idIdx = headers.indexOf('id');
  for (let i = 1; i < rows.length; i++) {
    if (String(rows[i][idIdx]) === String(data.id)) {
      sheet.deleteRow(i + 1);
      return jsonResponse({ success: true });
    }
  }
  return jsonResponse({ error: 'Record not found' });
}

// 헤더가 없으면 자동 생성
function getOrCreateHeaders(sheet) {
  const HEADERS = [
    'id', 'timestamp', 'date', 'slots', 'slot', 'slotLabel',
    'name', 'org', 'phone', 'email',
    'purpose', 'count', 'note', 'status'
  ];
  const firstRow = sheet.getRange(1, 1, 1, HEADERS.length).getValues()[0];
  if (!firstRow[0]) {
    sheet.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]);
    // 헤더 행 스타일
    const headerRange = sheet.getRange(1, 1, 1, HEADERS.length);
    headerRange.setBackground('#3a5035');
    headerRange.setFontColor('#ffffff');
    headerRange.setFontWeight('bold');
    sheet.setFrozenRows(1);
  }
  return HEADERS;
}

function jsonResponse(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
