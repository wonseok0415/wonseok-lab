// FieldCheck 진행 보고 PPT 생성기
//
// 내용의 원본은 PROGRESS_REPORT.md 이고, 이 파일은 그 내용을 슬라이드로
// 옮기는 스크립트다. 보고 내용이 바뀌면 PROGRESS_REPORT.md를 먼저 고치고
// 여기에 반영한다 (숫자가 두 곳에서 갈리지 않게 하기 위함).
//
//   npm install pptxgenjs
//   node build_report_deck.js FieldCheck_진행보고_YYYYMMDD.pptx
//
// 팔레트는 ThinQ Real 디자인 시스템(--c-accent #3a5035)과 관리자 페이지
// 자동 점검 탭의 톤다운 팔레트를 따른다.

const pptxgen = require('pptxgenjs');

// ── ThinQ Real 브랜드 기반 팔레트 (관리자 페이지 톤다운 팔레트와 동일 계열) ──
const OLIVE_DEEP = '202C1B';
const OLIVE      = '3A5035';   // --c-accent
const OLIVE_MID  = '5C7355';
const SAGE       = '97AC8E';
const BG_SOFT    = 'F4F6F2';
const WHITE      = 'FFFFFF';
const INK        = '1F2420';
const MUTED      = '6E786B';
const AMBER      = 'A8803A';
const BRICK      = '9C4A40';

const F  = '맑은 고딕';
const W = 13.3, H = 7.5;

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';
pres.author = 'ThinQ Real';
pres.title = 'FieldCheck 진행 보고';

const shadow = () => ({ type: 'outer', color: '000000', blur: 10, offset: 2, angle: 90, opacity: 0.10 });

// 표준 슬라이드 헤더 (제목 + 부제)
function head(s, title, sub, dark) {
  s.addText(title, {
    x: 0.7, y: 0.42, w: 11.9, h: 0.72, margin: 0,
    fontFace: F, fontSize: 32, bold: true, color: dark ? WHITE : INK,
  });
  if (sub) s.addText(sub, {
    x: 0.7, y: 1.16, w: 11.9, h: 0.4, margin: 0,
    fontFace: F, fontSize: 14, color: dark ? SAGE : MUTED,
  });
}

// 라운드 카드
function card(s, o) {
  s.addShape(pres.ShapeType.roundRect, {
    x: o.x, y: o.y, w: o.w, h: o.h, rectRadius: 0.09,
    fill: { color: o.fill || WHITE },
    line: o.line ? { color: o.line, width: 1 } : { color: 'E4E8E1', width: 1 },
    shadow: o.flat ? undefined : shadow(),
  });
}

// 번호 배지
function badge(s, x, y, txt, bg, fg) {
  s.addShape(pres.ShapeType.ellipse, {
    x, y, w: 0.42, h: 0.42, fill: { color: bg || OLIVE }, line: { color: bg || OLIVE, width: 0 },
  });
  s.addText(txt, {
    x, y, w: 0.42, h: 0.42, margin: 0,
    fontFace: F, fontSize: 13, bold: true, color: fg || WHITE,
    align: 'center', valign: 'middle',
  });
}

function slide(dark) {
  const s = pres.addSlide();
  s.background = { color: dark ? OLIVE_DEEP : WHITE };
  return s;
}

/* ══════════════ 1. 표지 ══════════════ */
{
  const s = slide(true);
  s.addShape(pres.ShapeType.ellipse, { x: 9.4, y: -2.2, w: 6.6, h: 6.6, fill: { color: OLIVE }, line: { width: 0 } });
  s.addShape(pres.ShapeType.ellipse, { x: 11.0, y: 4.3, w: 3.4, h: 3.4, fill: { color: OLIVE_MID }, line: { width: 0 } });

  s.addText('ThinQ Real · 운영 보고', {
    x: 0.9, y: 1.85, w: 8, h: 0.4, margin: 0,
    fontFace: F, fontSize: 15, color: SAGE, charSpacing: 2,
  });
  s.addText('FieldCheck', {
    x: 0.9, y: 2.35, w: 9, h: 1.15, margin: 0,
    fontFace: F, fontSize: 66, bold: true, color: WHITE,
  });
  s.addText('ThinQ ON Field 자동 점검 시스템', {
    x: 0.9, y: 3.5, w: 9, h: 0.6, margin: 0,
    fontFace: F, fontSize: 26, color: SAGE,
  });
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.92, y: 4.5, w: 4.75, h: 0.62, rectRadius: 0.31,
    fill: { color: OLIVE }, line: { color: OLIVE_MID, width: 1 },
  });
  s.addText('매일 아침 07:30 자동 운영 중', {
    x: 0.92, y: 4.5, w: 4.75, h: 0.62, margin: 0,
    fontFace: F, fontSize: 15, bold: true, color: WHITE, align: 'center', valign: 'middle',
  });
  s.addText('2026. 08. 02.   |   작성: 강원석', {
    x: 0.9, y: 5.6, w: 8, h: 0.4, margin: 0,
    fontFace: F, fontSize: 14, color: '8C9887',
  });
  s.addNotes('7/27 ATOM TTS 장애를 계기로 시작해 6일 만에 자동 운영에 들어간 점검 시스템 보고입니다.');
}

/* ══════════════ 2. 한 장 요약 ══════════════ */
{
  const s = slide(true);
  s.addText('“이번 사항을 시스템화 할 수 없는지”', {
    x: 0.7, y: 0.5, w: 11.9, h: 0.45, margin: 0,
    fontFace: F, fontSize: 16, color: SAGE, italic: true,
  });
  s.addText('됩니다. 이미 매일 아침 스스로 돌고 있습니다.', {
    x: 0.7, y: 1.02, w: 11.9, h: 0.85, margin: 0,
    fontFace: F, fontSize: 38, bold: true, color: WHITE,
  });

  const stats = [
    ['6일', '지시 → 자동 운영', '07-27 장애 → 08-02'],
    ['0원', '신규 비용', '유휴 노트북 + 기존 인프라'],
    ['6건 / 0건', '일일 판정 / 실패', 'L1 3건 + L2 3건'],
    ['1통', '사람이 볼 것', '아침 요약 메일'],
  ];
  stats.forEach((t, i) => {
    const x = 0.7 + i * 3.03;
    card(s, { x, y: 2.45, w: 2.83, h: 1.9, fill: OLIVE, line: OLIVE_MID, flat: true });
    s.addText(t[0], { x: x + 0.2, y: 2.64, w: 2.45, h: 0.66, margin: 0, fontFace: F, fontSize: 30, bold: true, color: WHITE });
    s.addText(t[1], { x: x + 0.2, y: 3.34, w: 2.45, h: 0.34, margin: 0, fontFace: F, fontSize: 13, bold: true, color: SAGE });
    s.addText(t[2], { x: x + 0.2, y: 3.7, w: 2.45, h: 0.45, margin: 0, fontFace: F, fontSize: 11, color: '8C9887' });
  });

  card(s, { x: 0.7, y: 4.68, w: 11.9, h: 1.95, fill: '2A3823', line: OLIVE_MID, flat: true });
  s.addText('장애를 사람이 눈치채기 전에 시스템이 먼저 보고합니다', {
    x: 1.05, y: 4.98, w: 11.2, h: 0.46, margin: 0,
    fontFace: F, fontSize: 20, bold: true, color: WHITE,
  });
  s.addText(
    '7월 장애는 월요일 오후에 시작해 화요일 아침에야 「시연 불가」로 발견됐습니다.\n' +
    '지금 구조라면 월요일 저녁 요약에서 잡힙니다 — 반나절 이상 빠릅니다.',
    { x: 1.05, y: 5.54, w: 11.2, h: 0.95, margin: 0, fontFace: F, fontSize: 15, color: SAGE, lineSpacing: 24 }
  );
  s.addNotes('보고의 결론을 먼저 제시합니다. 팀장님 질문에 대한 직접적인 답입니다.');
}

/* ══════════════ 3. 왜 만들었나 ══════════════ */
{
  const s = slide();
  head(s, '왜 만들었나', '2026-07-27 주간 · ATOM TTS 서버 장애');

  const tl = [
    ['월 오후', '무응답 증가', '발화 후 응답 없음\n빈도가 늘기 시작', MUTED],
    ['화 오전', '시연 불가', '일반 고객 가정에서도\n동일 증상 재현', BRICK],
    ['화 12시', '복구', 'CTO부문 LG TTS\n대안 확보', OLIVE],
  ];
  tl.forEach((t, i) => {
    const x = 0.7 + i * 3.35;
    card(s, { x, y: 1.75, w: 3.05, h: 1.95 });
    s.addText(t[0], { x: x + 0.25, y: 1.95, w: 2.55, h: 0.3, margin: 0, fontFace: F, fontSize: 12, bold: true, color: t[3] });
    s.addText(t[1], { x: x + 0.25, y: 2.28, w: 2.55, h: 0.42, margin: 0, fontFace: F, fontSize: 20, bold: true, color: INK });
    s.addText(t[2], { x: x + 0.25, y: 2.78, w: 2.55, h: 0.75, margin: 0, fontFace: F, fontSize: 12.5, color: MUTED, lineSpacing: 18 });
    if (i < 2) s.addText('▶', { x: x + 3.05, y: 2.5, w: 0.3, h: 0.4, margin: 0, fontFace: F, fontSize: 13, color: SAGE, align: 'center' });
  });

  card(s, { x: 10.75, y: 1.75, w: 1.85, h: 1.95, fill: BG_SOFT, flat: true });
  s.addText('반나절\n늦게 발견', { x: 10.9, y: 2.35, w: 1.55, h: 0.8, margin: 0, fontFace: F, fontSize: 17, bold: true, color: BRICK, align: 'center', lineSpacing: 24 });

  card(s, { x: 0.7, y: 4.0, w: 11.9, h: 1.15, fill: BG_SOFT, flat: true });
  s.addText('경영진 지시', { x: 1.0, y: 4.2, w: 2.0, h: 0.3, margin: 0, fontFace: F, fontSize: 12, bold: true, color: OLIVE });
  s.addText('“단건 해결에 그치지 말고, ThinQ ON 서비스 운영을 체계적으로 모니터링·대응하는 운영 프로세스를 즉시 수립할 것”', {
    x: 1.0, y: 4.5, w: 11.3, h: 0.45, margin: 0, fontFace: F, fontSize: 15, italic: true, color: INK,
  });

  s.addText('이 장애가 준 힌트', { x: 0.7, y: 5.42, w: 3, h: 0.35, margin: 0, fontFace: F, fontSize: 15, bold: true, color: OLIVE });
  s.addText(
    '증상이 “말을 걸었는데 답이 없다”였습니다. 즉 주기적으로 말을 걸어 답이 오는지만 봐도 알 수 있었습니다.\n' +
    '복잡한 감시 체계가 아니라 「매일 아침 대신 말을 걸어주는 장치」면 충분하다는 판단에서 출발했습니다.',
    { x: 0.7, y: 5.8, w: 11.9, h: 0.9, margin: 0, fontFace: F, fontSize: 14.5, color: INK, lineSpacing: 24 }
  );
  s.addNotes('장애 자체보다, 그 장애가 아주 단순한 방법으로 조기 감지 가능했다는 점이 출발점입니다.');
}

/* ══════════════ 4. 전체 구조 ══════════════ */
{
  const s = slide();
  head(s, '무엇을 만들었나', '기존 예약 관리 시스템의 백엔드·메일 인프라를 그대로 재활용 — 신규 서버·계정·과금 없음');

  const rows = [
    ['점검 장비', '상주 노트북 + (3단계) USB 웹캠', '① 음성 재생 "하이엘지" → 점검 질문   ② 내장 마이크로 응답 녹음   ③ 웹캠으로 가전 제어 전·후 촬영', OLIVE],
    ['판정', '점검 장비에서 즉시 실행', 'L1 응답 유무·시간   /   L2 내용 정확성 (로컬 STT)   /   L3 실제 동작', OLIVE_MID],
    ['기록', 'Apps Script → Google Sheets', 'health_checks 탭에 판정 결과·응답 시간·인식 문장 누적', SAGE],
    ['보고', '메일 + 관리자 페이지', '매일 아침 요약 메일 1통   +   관리자 🩺 자동 점검 탭', OLIVE],
  ];
  rows.forEach((r, i) => {
    const y = 1.78 + i * 1.22;
    card(s, { x: 0.7, y, w: 11.9, h: 1.02 });
    s.addShape(pres.ShapeType.roundRect, { x: 0.7, y, w: 1.75, h: 1.02, rectRadius: 0.09, fill: { color: r[3] }, line: { color: r[3], width: 0 } });
    s.addText(r[0], { x: 0.7, y, w: 1.75, h: 1.02, margin: 0, fontFace: F, fontSize: 16, bold: true, color: WHITE, align: 'center', valign: 'middle' });
    s.addText(r[1], { x: 2.65, y: y + 0.14, w: 9.7, h: 0.32, margin: 0, fontFace: F, fontSize: 13, bold: true, color: INK });
    s.addText(r[2], { x: 2.65, y: y + 0.5, w: 9.7, h: 0.42, margin: 0, fontFace: F, fontSize: 12.5, color: MUTED });
    if (i < 3) s.addText('▼', { x: 1.42, y: y + 1.0, w: 0.3, h: 0.22, margin: 0, fontFace: F, fontSize: 10, color: SAGE, align: 'center' });
  });
  s.addNotes('신규 인프라 없이 기존 시스템 위에 얹었다는 점이 비용 0원의 근거입니다.');
}

/* ══════════════ 5. 하루가 어떻게 돌아가는가 ══════════════ */
{
  const s = slide();
  head(s, '하루가 어떻게 돌아가는가', '사람이 할 일은 아침에 메일 한 번 보는 것뿐입니다');

  const day = [
    ['07:30', '자동 점검', '점검 장비가 스스로 깨어나\nThinQ ON에게 3개 질문\n→ 판정 후 서버 전송', '사람 할 일 없음', OLIVE],
    ['08시대', '요약 메일', '정상 / 실패가\n헤더 색으로 구분되어\n메일로 도착', '메일 한 번 보기', AMBER],
    ['상시', '관리자 페이지', '🩺 자동 점검 탭에서\n최근 7 / 14 / 30일\n추이 확인', '필요할 때만', OLIVE_MID],
    ['예약 시간', '자동 스킵', '확정 예약·차단 슬롯에는\n점검을 걸지 않음\n(시작 20분 전 ~ 종료 10분 후)', '사람 할 일 없음', SAGE],
  ];
  day.forEach((d, i) => {
    const x = 0.7 + i * 3.03;
    card(s, { x, y: 1.8, w: 2.83, h: 3.4 });
    s.addShape(pres.ShapeType.roundRect, { x, y: 1.8, w: 2.83, h: 0.62, rectRadius: 0.09, fill: { color: d[4] }, line: { color: d[4], width: 0 } });
    s.addText(d[0], { x: x + 0.18, y: 1.8, w: 2.47, h: 0.62, margin: 0, fontFace: F, fontSize: 16, bold: true, color: WHITE, valign: 'middle' });
    s.addText(d[1], { x: x + 0.22, y: 2.58, w: 2.4, h: 0.36, margin: 0, fontFace: F, fontSize: 17, bold: true, color: INK });
    s.addText(d[2], { x: x + 0.22, y: 3.02, w: 2.4, h: 1.25, margin: 0, fontFace: F, fontSize: 12.5, color: MUTED, lineSpacing: 18 });
    s.addShape(pres.ShapeType.roundRect, { x: x + 0.22, y: 4.42, w: 2.4, h: 0.44, rectRadius: 0.22, fill: { color: BG_SOFT }, line: { width: 0 } });
    s.addText(d[3], { x: x + 0.22, y: 4.42, w: 2.4, h: 0.44, margin: 0, fontFace: F, fontSize: 11.5, bold: true, color: OLIVE, align: 'center', valign: 'middle' });
  });

  card(s, { x: 0.7, y: 5.45, w: 11.9, h: 1.2, fill: BG_SOFT, flat: true });
  s.addText('왜 07:30인가', { x: 1.0, y: 5.62, w: 2.2, h: 0.3, margin: 0, fontFace: F, fontSize: 13, bold: true, color: OLIVE });
  s.addText('1회차 예약(09:00)의 회피 구간(08:40~)보다 앞서 시연과 충돌하지 않고, 08시 요약 메일에 당일 결과가 실립니다.\n즉 시연이 시작되기 전에 「오늘 정상」을 확인할 수 있습니다.', {
    x: 1.0, y: 5.95, w: 11.3, h: 0.62, margin: 0, fontFace: F, fontSize: 13.5, color: INK, lineSpacing: 20,
  });
  s.addNotes('팀원 입장에서 실제로 무엇이 바뀌는지를 보여주는 슬라이드입니다.');
}

/* ══════════════ 6. 판정 3단계 ══════════════ */
{
  const s = slide();
  head(s, '판정 3단계 — 무엇을 잡는가', '단계마다 보는 계층이 다릅니다. 어느 단계에서 실패했는지가 곧 원인 진단입니다');

  const lv = [
    ['L1', '말을 했는가', '소리 에너지만 분석\nSTT 불필요 · 즉시 판정', '7월 ATOM 장애가\n정확히 이 단계', '운영 중', OLIVE],
    ['L2', '맞는 말을 했는가', '녹음 → 로컬 STT\n→ 기대 키워드 대조', '오응답, "죄송해요\n모르겠어요", 연동 장애', '운영 중', OLIVE_MID],
    ['L3', '실제로 움직였는가', '가전 제어 전·후\n촬영 이미지 비교', '제어 경로 장애\n루틴 미실행', '설계 완료', SAGE],
  ];
  lv.forEach((l, i) => {
    const x = 0.7 + i * 4.07;
    card(s, { x, y: 1.8, w: 3.82, h: 3.32 });
    s.addShape(pres.ShapeType.roundRect, { x: x + 0.28, y: 2.05, w: 0.92, h: 0.55, rectRadius: 0.12, fill: { color: l[5] }, line: { width: 0 } });
    s.addText(l[0], { x: x + 0.28, y: 2.05, w: 0.92, h: 0.55, margin: 0, fontFace: F, fontSize: 20, bold: true, color: WHITE, align: 'center', valign: 'middle' });
    s.addText(l[4], { x: x + 2.4, y: 2.12, w: 1.15, h: 0.42, margin: 0, fontFace: F, fontSize: 11.5, bold: true, color: i < 2 ? OLIVE : MUTED, align: 'right', valign: 'middle' });
    s.addText(l[1], { x: x + 0.28, y: 2.78, w: 3.26, h: 0.42, margin: 0, fontFace: F, fontSize: 19, bold: true, color: INK });
    s.addText(l[2], { x: x + 0.28, y: 3.3, w: 3.26, h: 0.72, margin: 0, fontFace: F, fontSize: 12.5, color: MUTED, lineSpacing: 18 });
    s.addShape(pres.ShapeType.roundRect, { x: x + 0.28, y: 4.08, w: 3.26, h: 0.88, rectRadius: 0.09, fill: { color: BG_SOFT }, line: { width: 0 } });
    s.addText(l[3], { x: x + 0.45, y: 4.08, w: 2.92, h: 0.88, margin: 0, fontFace: F, fontSize: 12.5, bold: true, color: INK, valign: 'middle', lineSpacing: 18 });
  });

  const diag = [
    ['L1 실패', '소리가 안 남', 'TTS 서버 · 네트워크 · 기기'],
    ['L2 실패', '말은 하는데 엉뚱함', 'NLU · 엔진 · 외부 연동'],
    ['L3 실패', '말은 맞는데 안 움직임', '가전 제어 경로'],
  ];
  s.addText('실패 지점이 곧 원인 계층입니다', { x: 0.7, y: 5.32, w: 5, h: 0.32, margin: 0, fontFace: F, fontSize: 14, bold: true, color: OLIVE });
  diag.forEach((d, i) => {
    const x = 0.7 + i * 4.07;
    card(s, { x, y: 5.7, w: 3.82, h: 0.95, fill: BG_SOFT, flat: true });
    s.addText([
      { text: d[0], options: { bold: true, color: INK } },
      { text: '   ' + d[1], options: { color: MUTED } },
    ], { x: x + 0.25, y: 5.82, w: 3.32, h: 0.32, margin: 0, fontFace: F, fontSize: 12 });
    s.addText('→  ' + d[2], { x: x + 0.25, y: 6.18, w: 3.32, h: 0.34, margin: 0, fontFace: F, fontSize: 12.5, bold: true, color: OLIVE });
  });
  s.addNotes('한 덩어리로 "실패"라고만 적으면 원인 구분이 사라집니다. 3단계로 나눈 실익이 여기 있습니다.');
}

/* ══════════════ 7. L1 vs L2 ══════════════ */
{
  const s = slide();
  head(s, 'L1과 L2는 무엇이 다른가', '가장 많이 받는 질문입니다');

  card(s, { x: 0.7, y: 1.72, w: 11.9, h: 0.95, fill: OLIVE, line: OLIVE, flat: true });
  s.addText('전화에 비유하면 — L1은 "전화를 받았는가", L2는 "받아서 제대로 대답했는가"', {
    x: 1.0, y: 1.72, w: 11.3, h: 0.95, margin: 0, fontFace: F, fontSize: 19, bold: true, color: WHITE, valign: 'middle',
  });

  const hdr = ['상황', 'L1 응답 감지', 'L2 내용 판정'];
  const colX = [0.7, 5.6, 9.1];
  const colW = [4.8, 3.4, 3.5];
  hdr.forEach((h, i) => {
    s.addText(h, { x: colX[i] + 0.22, y: 2.88, w: colW[i] - 0.44, h: 0.34, margin: 0, fontFace: F, fontSize: 12.5, bold: true, color: MUTED });
  });

  const rows = [
    ['정상 응답', '통과', OLIVE, '통과', OLIVE, false],
    ['"죄송해요, 잘 모르겠어요"', '통과', AMBER, '실패', BRICK, true],
    ['무응답 (7월 ATOM 장애)', '실패', BRICK, '판정 안 함', MUTED, false],
  ];
  rows.forEach((r, i) => {
    const y = 3.3 + i * 0.86;
    card(s, { x: 0.7, y, w: 11.9, h: 0.72, fill: r[5] ? BG_SOFT : WHITE, flat: true, line: r[5] ? SAGE : 'E4E8E1' });
    s.addText(r[0], { x: 0.92, y, w: 4.55, h: 0.72, margin: 0, fontFace: F, fontSize: 14, bold: r[5], color: INK, valign: 'middle' });
    s.addText(r[1], { x: 5.82, y, w: 3.0, h: 0.72, margin: 0, fontFace: F, fontSize: 14, bold: true, color: r[2], valign: 'middle' });
    s.addText(r[3], { x: 9.32, y, w: 3.1, h: 0.72, margin: 0, fontFace: F, fontSize: 14, bold: true, color: r[4], valign: 'middle' });
  });

  s.addText([
    { text: '두 번째 줄이 L2의 존재 이유입니다. ', options: { bold: true, color: INK } },
    { text: 'ThinQ ON이 "죄송해요"라고 답하면 소리는 났으므로 L1은 통과합니다 — 이 유형은 L1으로는 원리상 잡을 수 없습니다.', options: { color: MUTED } },
  ], { x: 0.7, y: 5.95, w: 11.9, h: 0.45, margin: 0, fontFace: F, fontSize: 13.5 });
  s.addText('※ L2는 L1을 통과한 건에만 판정합니다. 따라서 L2 성공률은 “응답한 것 중 내용까지 맞은 비율”로 읽습니다.', {
    x: 0.7, y: 6.42, w: 11.9, h: 0.35, margin: 0, fontFace: F, fontSize: 12, color: MUTED,
  });
  s.addNotes('무응답을 L1·L2 두 건으로 세면 통계가 왜곡되므로 L2는 L1 통과 건에만 돌립니다.');
}

/* ══════════════ 8. 응답 시작 도식 ══════════════ */
{
  const s = slide();
  head(s, "'응답 시작'이란 무엇인가", '메일과 대시보드에 나오는 밀리초(ms) 수치가 무엇을 재는지');

  const steps = [
    ['①', '"하이엘지"\n재생', SAGE],
    ['②', "1.5초 대기\n('띵' 반응)", SAGE],
    ['③', '점검 질문\n재생', SAGE],
    ['④', '재생 끝\n= 0ms', OLIVE],
    ['⑤', 'ThinQ ON\n발화 시작', OLIVE],
  ];
  steps.forEach((st, i) => {
    const x = 0.7 + i * 2.44;
    card(s, { x, y: 1.9, w: 2.2, h: 1.5, fill: i >= 3 ? OLIVE : WHITE, line: i >= 3 ? OLIVE : 'E4E8E1' });
    s.addText(st[0], { x: x + 0.18, y: 2.05, w: 0.5, h: 0.35, margin: 0, fontFace: F, fontSize: 15, bold: true, color: i >= 3 ? WHITE : SAGE });
    s.addText(st[1], { x: x + 0.18, y: 2.45, w: 1.85, h: 0.8, margin: 0, fontFace: F, fontSize: 13.5, bold: true, color: i >= 3 ? WHITE : INK, lineSpacing: 19 });
    if (i < 4) s.addText('▶', { x: x + 2.2, y: 2.45, w: 0.24, h: 0.4, margin: 0, fontFace: F, fontSize: 12, color: SAGE, align: 'center' });
  });

  s.addShape(pres.ShapeType.roundRect, { x: 8.02, y: 3.55, w: 4.58, h: 0.5, rectRadius: 0.25, fill: { color: AMBER }, line: { width: 0 } });
  s.addText('◀   이 구간을 잽니다   ▶', { x: 8.02, y: 3.55, w: 4.58, h: 0.5, margin: 0, fontFace: F, fontSize: 13.5, bold: true, color: WHITE, align: 'center', valign: 'middle' });

  card(s, { x: 0.7, y: 4.32, w: 5.85, h: 1.05, fill: BG_SOFT, flat: true });
  s.addText('✓  질문을 다 말한 순간부터 답을 시작하기까지', { x: 0.95, y: 4.32, w: 5.4, h: 1.05, margin: 0, fontFace: F, fontSize: 14.5, bold: true, color: OLIVE, valign: 'middle' });
  card(s, { x: 6.75, y: 4.32, w: 5.85, h: 1.05, fill: BG_SOFT, flat: true });
  s.addText('✕  답변을 끝내기까지의 총 길이가 아닙니다', { x: 7.0, y: 4.32, w: 5.4, h: 1.05, margin: 0, fontFace: F, fontSize: 14.5, bold: true, color: MUTED, valign: 'middle' });

  card(s, { x: 0.7, y: 5.62, w: 11.9, h: 1.15, fill: WHITE, line: AMBER });
  s.addText("'띵' 반응은 일부러 측정하지 않습니다", { x: 1.0, y: 5.78, w: 11.3, h: 0.32, margin: 0, fontFace: F, fontSize: 14, bold: true, color: AMBER });
  s.addText('ATOM 장애가 “기동어는 듣고 띵도 내지만 말을 못 하는” 상태였습니다. 띵을 기준으로 삼았다면 그 장애를 정상으로 판정했을 것입니다.', {
    x: 1.0, y: 6.14, w: 11.3, h: 0.45, margin: 0, fontFace: F, fontSize: 13.5, color: INK,
  });
  s.addNotes('숫자만 있고 정의가 없으면 오해되므로 요약 메일 안에도 같은 도식을 넣었습니다.');
}

/* ══════════════ 9. 현장에서 해결한 문제 ══════════════ */
{
  const s = slide();
  head(s, '현장에서 발견하고 해결한 문제', '설계실에서는 나오지 않고 현장에서만 나온 문제들입니다 — 신뢰도의 근거');

  const issues = [
    ['기동어 직후 명령이 씹힘', "ThinQ ON이 '띵' 반응 전에는 듣지 못함", '기동어·질문을 분리 재생 + 1.5초 대기'],
    ["연산 대기음('띵띵띵')을 응답으로 오판", 'TTS 장애를 정상으로 판정할 구멍', '발성 비율 판정 — 1초 창의 70% 이상이 소리일 때만 말소리로 인정'],
    ['긴 답변이 다음 점검의 기동어를 씹음', '생성형이라 답변 길이가 크게 변동', '시나리오 사이 “조용해질 때까지 대기” — 판정 결과와 무관하게 항상'],
    ['소음 환경에서 정상 응답을 실패로 오판', '절대 음량 기준이 에어컨·선풍기 소음 위로 잡힘', '적응형 판정 — 음성 대역만 측정 + 기저 소음 자동 추정 + 기저 +8dB'],
  ];
  issues.forEach((it, i) => {
    const y = 1.8 + i * 1.2;
    card(s, { x: 0.7, y, w: 11.9, h: 1.0 });
    badge(s, 0.95, y + 0.29, String(i + 1));
    s.addText(it[0], { x: 1.55, y: y + 0.12, w: 4.35, h: 0.38, margin: 0, fontFace: F, fontSize: 14.5, bold: true, color: INK, valign: 'middle' });
    s.addText(it[1], { x: 1.55, y: y + 0.52, w: 4.35, h: 0.36, margin: 0, fontFace: F, fontSize: 11.5, color: MUTED, valign: 'middle' });
    s.addText('→', { x: 6.0, y, w: 0.35, h: 1.0, margin: 0, fontFace: F, fontSize: 14, color: SAGE, align: 'center', valign: 'middle' });
    s.addText(it[2], { x: 6.45, y, w: 5.95, h: 1.0, margin: 0, fontFace: F, fontSize: 13, color: OLIVE, bold: true, valign: 'middle' });
  });

  s.addText('그리고 가장 위험했던 다섯 번째 — 다음 장', {
    x: 0.7, y: 6.72, w: 11.9, h: 0.35, margin: 0, fontFace: F, fontSize: 13, bold: true, color: AMBER,
  });
  s.addNotes('현장 검증에서만 드러난 문제들이라, 실제로 돌려보지 않았으면 전부 놓쳤을 항목입니다.');
}

/* ══════════════ 10. 마이크 권한 함정 ══════════════ */
{
  const s = slide();
  head(s, '가장 위험했던 사례 — 점검 장비가 스스로를 속인 경우');

  card(s, { x: 0.7, y: 1.6, w: 11.9, h: 0.92, fill: BRICK, line: BRICK, flat: true });
  s.addText('자동 실행 첫날 점검 3건 전부 실패 — 그런데 ThinQ ON은 정상이었습니다', {
    x: 1.0, y: 1.6, w: 11.3, h: 0.92, margin: 0, fontFace: F, fontSize: 19, bold: true, color: WHITE, valign: 'middle',
  });

  const box = [
    ['원인', 'macOS는 앱이 아닌 실행 파일(python)에는 마이크 권한 창을 띄우지 않고, 오류도 없이 무음을 반환합니다.\n시스템 설정 목록에도 나타나지 않아 수동 허용조차 불가능했습니다.', BRICK],
    ['판별 단서', '세 시나리오의 소음 측정값이 소수점까지 동일(2.4 / −32.6 dBA)하고 최고값이 기저값보다 낮았습니다.\n보정값을 빼면 −120dB — 에너지가 정확히 0, 즉 완전한 디지털 무음이었습니다.', AMBER],
    ['해결', '① 정식 앱(터미널)을 경유해 실행 → 권한 창이 정상 표시\n② 무음 자동 감지 → “점검 장비 설정/권한 문제(ThinQ ON 장애 아님)”로 별도 표기   ③ 진단 명령 추가', OLIVE],
  ];
  box.forEach((b, i) => {
    const y = 2.72 + i * 1.15;
    card(s, { x: 0.7, y, w: 11.9, h: 0.98 });
    s.addShape(pres.ShapeType.roundRect, { x: 0.7, y, w: 1.5, h: 0.98, rectRadius: 0.09, fill: { color: b[2] }, line: { width: 0 } });
    s.addText(b[0], { x: 0.7, y, w: 1.5, h: 0.98, margin: 0, fontFace: F, fontSize: 14, bold: true, color: WHITE, align: 'center', valign: 'middle' });
    s.addText(b[1], { x: 2.4, y, w: 9.95, h: 0.98, margin: 0, fontFace: F, fontSize: 12.5, color: INK, valign: 'middle', lineSpacing: 19 });
  });

  card(s, { x: 0.7, y: 6.18, w: 11.9, h: 0.85, fill: BG_SOFT, flat: true });
  s.addText([
    { text: '교훈 — ', options: { bold: true, color: OLIVE } },
    { text: '점검 시스템은 자기 자신의 고장을 스스로 진단할 수 있어야 합니다. 그러지 못하면 자기 고장을 대상의 장애로 오보합니다.', options: { bold: true, color: INK } },
  ], { x: 1.0, y: 6.18, w: 11.3, h: 0.85, margin: 0, fontFace: F, fontSize: 14.5, valign: 'middle' });
  s.addNotes('같은 원리를 L3에도 적용합니다 — 카메라 미연결·렌즈 가림을 가전 장애로 오보하지 않도록.');
}

/* ══════════════ 11. 검증 결과 ══════════════ */
{
  const s = slide();
  head(s, '검증 결과 (실측)', '2026-08-01 L1+L2 통합 판정 · 2026-08-02 자동 실행');

  const kpi = [
    ['6건', '일일 판정', 'L1 3건 + L2 3건'],
    ['0건', '실패', '전원 통과'],
    ['20건', '자체 시험', '전원 통과'],
    ['07:30', '자동 실행', '사람 개입 없이 성공'],
  ];
  kpi.forEach((k, i) => {
    const x = 0.7 + i * 3.03;
    card(s, { x, y: 1.78, w: 2.83, h: 1.35, fill: BG_SOFT, flat: true });
    s.addText(k[0], { x: x + 0.22, y: 1.9, w: 2.4, h: 0.55, margin: 0, fontFace: F, fontSize: 28, bold: true, color: OLIVE });
    s.addText(k[1], { x: x + 0.22, y: 2.47, w: 2.4, h: 0.3, margin: 0, fontFace: F, fontSize: 13, bold: true, color: INK });
    s.addText(k[2], { x: x + 0.22, y: 2.75, w: 2.4, h: 0.3, margin: 0, fontFace: F, fontSize: 11, color: MUTED });
  });

  s.addText('실제 인식 결과 — 로컬 STT가 받아쓴 ThinQ ON의 답변', { x: 0.7, y: 3.32, w: 8, h: 0.35, margin: 0, fontFace: F, fontSize: 14, bold: true, color: OLIVE });

  const cols = [[0.7, 3.5], [4.35, 1.6], [6.1, 5.15], [11.4, 1.2]];
  ['시나리오', '응답 시작', '인식된 문장', '판정'].forEach((h, i) => {
    s.addText(h, { x: cols[i][0] + 0.2, y: 3.72, w: cols[i][1] - 0.3, h: 0.3, margin: 0, fontFace: F, fontSize: 11.5, bold: true, color: MUTED });
  });
  const recs = [
    ['시간 질문', '150 ms', '"지금은 9시 33분이에요"'],
    ['일상 대화', '2,910 ms', '"저는 항상 기분이 좋아요…"'],
    ['날씨 (외부 연동)', '4,620 ms', '"오늘 등천동 날씨는… 기온은 최고 34.2도…"'],
  ];
  recs.forEach((r, i) => {
    const y = 4.08 + i * 0.72;
    card(s, { x: 0.7, y, w: 11.9, h: 0.6, flat: true });
    s.addText(r[0], { x: 0.9, y, w: 3.3, h: 0.6, margin: 0, fontFace: F, fontSize: 13, bold: true, color: INK, valign: 'middle' });
    s.addText(r[1], { x: 4.55, y, w: 1.4, h: 0.6, margin: 0, fontFace: F, fontSize: 13, color: OLIVE, bold: true, valign: 'middle' });
    s.addText(r[2], { x: 6.3, y, w: 4.95, h: 0.6, margin: 0, fontFace: F, fontSize: 12.5, color: MUTED, valign: 'middle' });
    s.addText('통과', { x: 11.6, y, w: 0.9, h: 0.6, margin: 0, fontFace: F, fontSize: 13, bold: true, color: OLIVE, valign: 'middle' });
  });

  card(s, { x: 0.7, y: 6.3, w: 11.9, h: 0.78, fill: BG_SOFT, flat: true });
  s.addText([
    { text: '받아쓰기 오류는 감수합니다 (의도된 설계) — ', options: { bold: true, color: OLIVE } },
    { text: '“등촌동”을 “등천동”으로 잘못 듣지만 기대 키워드(날씨·기온)가 살아남아 판정은 정확합니다. 키워드를 여러 개 두어 오인식 한 번이 오판정이 되지 않게 했습니다.', options: { color: INK } },
  ], { x: 1.0, y: 6.3, w: 11.3, h: 0.78, margin: 0, fontFace: F, fontSize: 12.5, valign: 'middle' });
  s.addNotes('판정 대상은 "질문에 맞는 답을 했는가"이지 "받아쓰기가 정확한가"가 아닙니다.');
}

/* ══════════════ 12. 무엇을 받게 되는가 ══════════════ */
{
  const s = slide();
  head(s, '무엇을 받게 되는가', '건별 알림은 없습니다 — 정상일 때는 아침 요약 한 통뿐입니다');

  card(s, { x: 0.7, y: 1.8, w: 5.85, h: 3.4 });
  s.addShape(pres.ShapeType.roundRect, { x: 0.7, y: 1.8, w: 5.85, h: 0.72, rectRadius: 0.09, fill: { color: OLIVE }, line: { width: 0 } });
  s.addText('①   매일 아침 요약 메일', { x: 1.0, y: 1.8, w: 5.25, h: 0.72, margin: 0, fontFace: F, fontSize: 17, bold: true, color: WHITE, valign: 'middle' });
  s.addText([
    { text: '헤더 색으로 상태 구분 — 정상은 올리브, 실패·기록 없음은 경고색', options: { bullet: true, breakLine: true } },
    { text: '판정 건수 · 성공률 · 평균 응답 시작 KPI + 단계별 성공률', options: { bullet: true, breakLine: true } },
    { text: '실패 시 [L1]/[L2] 배지 + 인식된 문장 + 사유 + 녹음 파일명', options: { bullet: true, breakLine: true } },
    { text: "'응답 시작' 측정 구간 도식을 메일 안에 포함", options: { bullet: true } },
  ], { x: 1.0, y: 2.72, w: 5.25, h: 2.3, margin: 0, fontFace: F, fontSize: 13, color: INK, paraSpaceAfter: 10, lineSpacing: 19 });

  card(s, { x: 6.75, y: 1.8, w: 5.85, h: 3.4 });
  s.addShape(pres.ShapeType.roundRect, { x: 6.75, y: 1.8, w: 5.85, h: 0.72, rectRadius: 0.09, fill: { color: OLIVE_MID }, line: { width: 0 } });
  s.addText('②   관리자 페이지 🩺 자동 점검 탭', { x: 7.05, y: 1.8, w: 5.25, h: 0.72, margin: 0, fontFace: F, fontSize: 17, bold: true, color: WHITE, valign: 'middle' });
  s.addText([
    { text: '오늘 상태 / L1·L2 성공률 / 평균 응답 시작', options: { bullet: true, breakLine: true } },
    { text: '일자별 성공률 — 점검이 없던 날은 빈칸으로 남겨 "안 돌았음"이 드러남', options: { bullet: true, breakLine: true } },
    { text: '단계·시나리오별 성공률, 최근 실패 20건', options: { bullet: true, breakLine: true } },
    { text: '기간 7 / 14 / 30일 전환', options: { bullet: true } },
  ], { x: 7.05, y: 2.72, w: 5.25, h: 2.3, margin: 0, fontFace: F, fontSize: 13, color: INK, paraSpaceAfter: 10, lineSpacing: 19 });

  card(s, { x: 0.7, y: 5.4, w: 11.9, h: 1.55, fill: OLIVE, line: OLIVE, flat: true });
  s.addText('침묵을 정상으로 오인하지 않습니다', { x: 1.0, y: 5.6, w: 11.3, h: 0.36, margin: 0, fontFace: F, fontSize: 17, bold: true, color: WHITE });
  s.addText('24시간 동안 점검 기록이 없으면 「점검 장비 미가동 의심」 경고가 나갑니다. 실제로 이 경고 덕분에 자동 실행이 빠져 있다는 것을 발견했습니다.\n※ 현재는 테스트 단계라 운영자 1인에게만 발송합니다. 정식 운영 시 담당자 전체로 전환합니다.', {
    x: 1.0, y: 6.02, w: 11.3, h: 0.85, margin: 0, fontFace: F, fontSize: 12.5, color: SAGE, lineSpacing: 19,
  });
  s.addNotes('알림 피로를 만들지 않는 것이 설계 원칙이었습니다. 매번 성공을 알리면 아무도 안 보게 됩니다.');
}

/* ══════════════ 13. 실패 메일을 받으면 ══════════════ */
{
  const s = slide();
  head(s, '실패 메일을 받으면 무엇을 하나', '팀원용 대응 가이드');

  const acts = [
    ['[L1] 무응답', 'ThinQ ON이 말을 하지 않음', '현장에서 직접 "하이엘지" 발화 → 재현되면 TTS·네트워크 이슈로 보고', BRICK],
    ['[L2] 실패', '말은 했는데 내용이 다름', '인식 문장 확인 → "죄송/모르겠" 계열이면 엔진 이슈, 날씨만 실패면 외부 연동 의심', AMBER],
    ['⚠ 점검 장비 설정/권한 문제', 'ThinQ ON 장애가 아님', '점검 장비의 마이크 권한·입력 장치 확인 (--mic-test 명령)', OLIVE_MID],
    ['⚠ 점검 기록 없음', '그날 한 번도 실행되지 않음', '점검 장비 전원·절전 상태 확인 (덮개만 닫고 전원 연결 유지)', OLIVE_MID],
  ];
  acts.forEach((a, i) => {
    const y = 1.8 + i * 1.16;
    card(s, { x: 0.7, y, w: 11.9, h: 0.98 });
    s.addShape(pres.ShapeType.roundRect, { x: 0.9, y: y + 0.26, w: 2.85, h: 0.46, rectRadius: 0.09, fill: { color: a[3] }, line: { width: 0 } });
    s.addText(a[0], { x: 0.9, y: y + 0.26, w: 2.85, h: 0.46, margin: 0, fontFace: F, fontSize: 12.5, bold: true, color: WHITE, align: 'center', valign: 'middle' });
    s.addText(a[1], { x: 4.0, y, w: 3.2, h: 0.98, margin: 0, fontFace: F, fontSize: 12.5, color: MUTED, valign: 'middle' });
    s.addText(a[2], { x: 7.35, y, w: 5.0, h: 0.98, margin: 0, fontFace: F, fontSize: 12.5, bold: true, color: INK, valign: 'middle', lineSpacing: 18 });
  });

  card(s, { x: 0.7, y: 6.5, w: 11.9, h: 0.62, fill: BG_SOFT, flat: true });
  s.addText([
    { text: '실패 1건이 곧 장애는 아닙니다. ', options: { bold: true, color: BRICK } },
    { text: '현장 재현 확인이 항상 첫 단계이고, 판단 근거가 되는 녹음 파일은 점검 장비에 그대로 남아 있습니다.', options: { color: INK } },
  ], { x: 1.0, y: 6.5, w: 11.3, h: 0.62, margin: 0, fontFace: F, fontSize: 13, valign: 'middle' });
  s.addNotes('팀원이 실제로 쓸 부분입니다. 메일 문구와 조치를 1:1로 대응시켰습니다.');
}

/* ══════════════ 14. 비용 + 남은 계획 ══════════════ */
{
  const s = slide();
  head(s, '비용과 남은 계획');

  s.addText('비용', { x: 0.7, y: 1.72, w: 3, h: 0.32, margin: 0, fontFace: F, fontSize: 15, bold: true, color: OLIVE });
  const costs = [
    ['점검 장비', '0원', '유휴 노트북 활용'],
    ['백엔드 · 메일', '0원', '기존 예약 시스템 재활용'],
    ['음성 인식(STT)', '0원', '로컬 실행 — 과금·계정 없음'],
    ['USB 웹캠 (3단계)', '수만 원', '유일한 신규 구매'],
  ];
  costs.forEach((c, i) => {
    const y = 2.12 + i * 0.76;
    card(s, { x: 0.7, y, w: 5.85, h: 0.64, flat: true });
    s.addText(c[0], { x: 0.92, y, w: 2.5, h: 0.64, margin: 0, fontFace: F, fontSize: 12.5, color: INK, valign: 'middle' });
    s.addText(c[1], { x: 3.5, y, w: 1.1, h: 0.64, margin: 0, fontFace: F, fontSize: 14, bold: true, color: i < 3 ? OLIVE : MUTED, valign: 'middle' });
    s.addText(c[2], { x: 4.68, y, w: 1.75, h: 0.64, margin: 0, fontFace: F, fontSize: 10.5, color: MUTED, valign: 'middle' });
  });

  s.addText('남은 계획', { x: 6.75, y: 1.72, w: 3, h: 0.32, margin: 0, fontFace: F, fontSize: 15, bold: true, color: OLIVE });
  const plans = [
    ['구축 3단계 (L3)', 'USB 웹캠으로 가전 제어 전·후 촬영 판정', '판정 방식 확정'],
    ['운영 전환', '상주 Windows 이관 + 단일 실행파일 패키징 + 담당자 전체 알림', '대기'],
    ['Phase 2 격상', '수동 일일 점검을 자동 점검으로 대체', '병행 검증 후'],
  ];
  plans.forEach((p, i) => {
    const y = 2.12 + i * 1.04;
    card(s, { x: 6.75, y, w: 5.85, h: 0.92 });
    badge(s, 6.98, y + 0.25, String(i + 1));
    s.addText(p[0], { x: 7.58, y: y + 0.1, w: 3.1, h: 0.34, margin: 0, fontFace: F, fontSize: 13.5, bold: true, color: INK, valign: 'middle' });
    s.addText(p[2], { x: 10.7, y: y + 0.1, w: 1.7, h: 0.34, margin: 0, fontFace: F, fontSize: 10.5, bold: true, color: OLIVE, align: 'right', valign: 'middle' });
    s.addText(p[1], { x: 7.58, y: y + 0.44, w: 4.8, h: 0.4, margin: 0, fontFace: F, fontSize: 11.5, color: MUTED, valign: 'middle' });
  });

  card(s, { x: 0.7, y: 5.38, w: 11.9, h: 1.6, fill: BG_SOFT, flat: true });
  s.addText('L3는 AI 엔진 없이 구현합니다', { x: 1.0, y: 5.56, w: 11.3, h: 0.34, margin: 0, fontFace: F, fontSize: 15, bold: true, color: OLIVE });
  s.addText(
    '카메라와 쇼룸 배치가 고정이므로 “무엇인지 인식”이 아니라 “달라졌는지 비교” 문제입니다 — 관심영역의 픽셀 차이 계산으로 충분합니다.\n' +
    'API 대신 카메라를 택한 이유: API는 “서버가 명령을 받았는가”만 봅니다. 명령은 접수됐는데 커튼 모터가 안 도는 경우, 방문객 눈에 보이는 것은 물리적 변화입니다.',
    { x: 1.0, y: 5.96, w: 11.3, h: 0.95, margin: 0, fontFace: F, fontSize: 12.5, color: INK, lineSpacing: 20 }
  );
  s.addNotes('3단계에 드는 신규 비용은 웹캠 1대뿐이고, AI 엔진 도입이 필요 없다는 점이 핵심입니다.');
}

/* ══════════════ 15. 마무리 ══════════════ */
{
  const s = slide(true);
  s.addShape(pres.ShapeType.ellipse, { x: -2.0, y: 3.6, w: 6.2, h: 6.2, fill: { color: OLIVE }, line: { width: 0 } });

  s.addText('요약', { x: 0.9, y: 0.9, w: 6, h: 0.55, margin: 0, fontFace: F, fontSize: 34, bold: true, color: WHITE });

  const pts = [
    ['7/27 장애 → 8/2 자동 운영', '지시받은 “체계적 모니터링·대응 프로세스”가 동작하는 형태로 존재합니다'],
    ['비용 0원', '유휴 노트북 + 기존 인프라 재활용. 신규 계정·과금 없음'],
    ['사람이 할 일은 아침 메일 한 번 보기', '판정·기록·보고는 전부 자동입니다'],
    ['침묵을 정상으로 오인하지 않습니다', '점검이 안 돌면 그 사실 자체가 보고됩니다'],
  ];
  pts.forEach((p, i) => {
    const y = 1.75 + i * 1.05;
    s.addShape(pres.ShapeType.roundRect, { x: 4.35, y, w: 8.25, h: 0.88, rectRadius: 0.09, fill: { color: '2A3823' }, line: { color: OLIVE_MID, width: 1 } });
    badge(s, 4.6, y + 0.23, String(i + 1), OLIVE, WHITE);
    s.addText(p[0], { x: 5.2, y: y + 0.1, w: 7.2, h: 0.34, margin: 0, fontFace: F, fontSize: 14.5, bold: true, color: WHITE, valign: 'middle' });
    s.addText(p[1], { x: 5.2, y: y + 0.44, w: 7.2, h: 0.34, margin: 0, fontFace: F, fontSize: 11.5, color: SAGE, valign: 'middle' });
  });

  s.addText('문의 · 강원석', { x: 0.9, y: 5.95, w: 3.2, h: 0.32, margin: 0, fontFace: F, fontSize: 14, bold: true, color: WHITE });
  s.addText('상세 설계·결정 이력은\nfieldcheck/DESIGN.md 참조', { x: 0.9, y: 6.32, w: 3.4, h: 0.6, margin: 0, fontFace: F, fontSize: 11.5, color: SAGE, lineSpacing: 17 });
  s.addNotes('질문 받고 마무리합니다.');
}

pres.writeFile({ fileName: process.argv[2] || 'FieldCheck_진행보고.pptx' })
  .then(f => console.log('생성 완료:', f));
