// FieldVoice 컨센서스 미팅 덱 (2장) — 내용 원본은 PROGRESS_REPORT.md (수정 시 md 먼저)
// 실행: node build_consensus_deck.js  →  FieldVoice_추진보고_20260820.pptx
const pptxgen = require("pptxgenjs");

const OLIVE = "3a5035";      // ThinQ Real 메인 컬러
const OLIVE_SOFT = "4a6244"; // 다크 배경 위 카드
const SOFT = "eef1ec";       // 라이트 배경 카드
const GOLD = "c9a35c";       // 어두운 배경 위 강조
const GOLD_DEEP = "a8803a";  // 밝은 배경 위 강조
const INK = "1d1d1f";
const GRAY = "6e6e73";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5

// ────────────────────────────────── Slide 1 — 무엇이고 왜 필요한가
{
  const s = pres.addSlide();
  s.background = { color: OLIVE };

  s.addText("FieldVoice", {
    x: 0.7, y: 0.42, w: 6.0, h: 0.75, margin: 0,
    fontFace: "Arial", fontSize: 40, bold: true, color: "FFFFFF",
  });
  s.addText("현장 목소리 수집·분석 시스템 — 방문 인터뷰를 데이터 자산으로", {
    x: 0.7, y: 1.14, w: 7.5, h: 0.4, margin: 0,
    fontFace: "Arial", fontSize: 15, color: GOLD,
  });

  // 왼쪽 — 왜 필요한가
  s.addText("왜 필요한가", {
    x: 0.7, y: 1.85, w: 5.2, h: 0.4, margin: 0,
    fontFace: "Arial", fontSize: 17, bold: true, color: GOLD,
  });
  s.addText([
    { text: "방문 후 설문은 기억·체면 필터를 거친 정제된 답변 — 시연 순간의 즉석 반응·질문·잡담은 증발", options: { bullet: true, breakLine: true, paraSpaceAfter: 10 } },
    { text: "공간 운영 3축(쇼룸 지원·기술 검증·데이터 축적) 중 '현장 발화 데이터'가 빈칸", options: { bullet: true, breakLine: true, paraSpaceAfter: 10 } },
    { text: "FieldCheck가 기계(ThinQ ON)의 상태를 매일 축적하듯, 사람의 목소리를 축적하는 짝 시스템", options: { bullet: true } },
  ], {
    x: 0.7, y: 2.28, w: 5.35, h: 2.1, margin: 0, valign: "top",
    fontFace: "Arial", fontSize: 12.5, color: "FFFFFF", lineSpacingMultiple: 1.15,
  });

  // 질문 철학 카드
  s.addText([
    { text: "“왜?”라고 묻지 않는다 — 제품이 아니라 삶을 묻는다", options: { italic: true, bold: true, fontSize: 14, color: "FFFFFF", breakLine: true, paraSpaceAfter: 6 } },
    { text: "자동차 업계 고객 리서치 방법론을 AI홈에 이식한 질문 프레임 (로망·부러움·아쉬움·경계·미래일기 5유형)", options: { fontSize: 10.5, color: "E3E9DF" } },
  ], {
    shape: pres.ShapeType.roundRect, rectRadius: 0.09,
    x: 0.7, y: 4.55, w: 5.35, h: 1.25, fill: { color: OLIVE_SOFT },
    margin: 0.14, valign: "middle", fontFace: "Arial",
  });

  // 하단 원칙 3줄
  const principles = [
    "추가 비용 0원 — 상주 노트북·구독형 AI·기존 백엔드 재활용",
    "개인정보 — 원본 음성은 현장 장비에만, 서버에는 가명화 요약만",
    "메인 시스템 무변경 — FieldCheck 선례의 순수 추가 방식",
  ];
  principles.forEach((t, i) => {
    s.addText("·  " + t, {
      x: 0.7, y: 6.0 + i * 0.42, w: 5.6, h: 0.38, margin: 0,
      fontFace: "Arial", fontSize: 11, color: "D7E0D2",
    });
  });

  // 오른쪽 — 동작 흐름 5단계
  s.addText("어떻게 동작하나", {
    x: 6.75, y: 1.85, w: 5.9, h: 0.4, margin: 0,
    fontFace: "Arial", fontSize: 17, bold: true, color: GOLD,
  });
  const steps = [
    ["현장 녹음", "도슨트가 시연 중 진행 — 시작 시 녹음 고지"],
    ["로컬 전사", "장비 안에서 음성→텍스트, 음성이 밖으로 나가지 않음"],
    ["AI 분석 4단계", "화자 라벨링 → 요약 → 맥락 분석 → 인사이트 도출"],
    ["1페이지 리포트", "한 줄 결론 · 인사이트 TOP5 · 개선 제안 — 2분 열람"],
    ["관리자 페이지 축적", "현장 인사이트 탭 — 관리자 3인 열람, 회차별 비교"],
  ];
  steps.forEach((st, i) => {
    const y = 2.32 + i * 0.94;
    s.addText(String(i + 1), {
      shape: pres.ShapeType.ellipse,
      x: 6.75, y: y + 0.17, w: 0.46, h: 0.46, fill: { color: GOLD },
      align: "center", valign: "middle", margin: 0,
      fontFace: "Arial", fontSize: 15, bold: true, color: OLIVE,
    });
    s.addText([
      { text: st[0], options: { bold: true, fontSize: 13.5, color: INK, breakLine: true, paraSpaceAfter: 2 } },
      { text: st[1], options: { fontSize: 10.5, color: GRAY } },
    ], {
      shape: pres.ShapeType.roundRect, rectRadius: 0.07,
      x: 7.4, y: y, w: 5.2, h: 0.8, fill: { color: "FFFFFF" },
      margin: 0.11, valign: "middle", fontFace: "Arial",
    });
  });

  s.addNotes("배경: 설문(사후·정제) vs 현장 발화(즉석·날것)의 보완 관계. FieldCheck와의 대구 — 기계 상태 vs 사람 목소리. 질문 프레임은 자동차 UX 리서치 방법론 이식. 비용 0원과 개인정보 설계(로컬 전사·가명 요약만 업로드)를 강조.");
}

// ────────────────────────────────── Slide 2 — 파일럿 결과 + 컨센서스 요청
{
  const s = pres.addSlide();
  s.background = { color: "FFFFFF" };

  s.addText("파일럿 검증 — 자동 분석, 믿어도 되는가", {
    x: 0.7, y: 0.45, w: 11.9, h: 0.6, margin: 0,
    fontFace: "Arial", fontSize: 30, bold: true, color: OLIVE,
  });
  s.addText("8/5 계열사 방문 76분 실녹음 파일럿 · 2026-08-20", {
    x: 0.7, y: 1.08, w: 11.9, h: 0.35, margin: 0,
    fontFace: "Arial", fontSize: 12, color: GRAY,
  });

  // 스탯 카드 3개
  const stats = [
    ["76분", "실녹음 전 과정 완주 — 녹음→전사→분석→리포트"],
    ["0원", "추가 비용 — 기존 노트북·구독형 AI·기존 백엔드"],
    ["+4건", "자동 분석이 전문 수동 판독을 초과 발견 (핵심 결론은 일치)"],
  ];
  stats.forEach((st, i) => {
    s.addText([
      { text: st[0], options: { bold: true, fontSize: 34, color: OLIVE, breakLine: true, paraSpaceAfter: 4 } },
      { text: st[1], options: { fontSize: 10.5, color: GRAY } },
    ], {
      shape: pres.ShapeType.roundRect, rectRadius: 0.09,
      x: 0.7 + i * 4.07, y: 1.62, w: 3.85, h: 1.5, fill: { color: SOFT },
      margin: 0.14, valign: "middle", fontFace: "Arial",
    });
  });

  // 왼쪽 — 인사이트 예시
  s.addText("파일럿이 실제로 낸 인사이트 (예시)", {
    x: 0.7, y: 3.5, w: 6.1, h: 0.4, margin: 0,
    fontFace: "Arial", fontSize: 16, bold: true, color: OLIVE,
  });
  s.addText([
    { text: "조명·커튼 자동화(저비용 구성)만으로 “집에 들어올 때의 기분”이 바뀌고 가사 분담까지 변화 — 정서 전환이 구매 동인이라는 서사 확보", options: { bullet: true, breakLine: true, paraSpaceAfter: 9 } },
    { text: "구축 아파트 개별 설치 불가가 방문객 관심이 이탈하는 정확한 지점으로 관측", options: { bullet: true, breakLine: true, paraSpaceAfter: 9 } },
    { text: "시연 운영 개선 3건 도출 — 대기 구간을 질문 슬롯으로, 녹음 고지 1회 제한, 자기개방 후 되묻기", options: { bullet: true, breakLine: true, paraSpaceAfter: 9 } },
    { text: "운영 모델 확정: 자동 분석 기본 + 사람 검수 1회(인용·가명화)", options: { bullet: true } },
  ], {
    x: 0.7, y: 3.95, w: 6.15, h: 2.85, margin: 0, valign: "top",
    fontFace: "Arial", fontSize: 12, color: INK, lineSpacingMultiple: 1.12,
  });

  // 오른쪽 — 결정 요청 3건
  s.addText("컨센서스 요청 — 결정 필요 3건", {
    x: 7.35, y: 3.5, w: 5.3, h: 0.4, margin: 0,
    fontFace: "Arial", fontSize: 16, bold: true, color: GOLD_DEEP,
  });
  const asks = [
    ["정식 운영 전환", "다음 회차부터 질문 프레임 실전 투입 + 회차별 리포트 축적"],
    ["녹음 동의 절차 확정", "현장 구두 고지 + 서면 1장 — 컴플라이언스 확인 경로 지정"],
    ["사내 Claude Code 신청", "공용 노트북에 개인 계정 상주 금지 원칙 — 이관 액션 #8 연계"],
  ];
  asks.forEach((a, i) => {
    const y = 3.95 + i * 1.03;
    s.addText(String(i + 1), {
      shape: pres.ShapeType.ellipse,
      x: 7.35, y: y + 0.21, w: 0.46, h: 0.46, fill: { color: OLIVE },
      align: "center", valign: "middle", margin: 0,
      fontFace: "Arial", fontSize: 15, bold: true, color: "FFFFFF",
    });
    s.addText([
      { text: a[0], options: { bold: true, fontSize: 13.5, color: INK, breakLine: true, paraSpaceAfter: 2 } },
      { text: a[1], options: { fontSize: 10.5, color: GRAY } },
    ], {
      shape: pres.ShapeType.roundRect, rectRadius: 0.07,
      x: 8.0, y: y, w: 4.65, h: 0.89, fill: { color: SOFT },
      margin: 0.11, valign: "middle", fontFace: "Arial",
    });
  });

  s.addText("구축 현황: 파이프라인·관리자 연동 코드 완료(머지) — Apps Script 재배포 1회 후 가동 · 상세: fieldvoice/PROGRESS_REPORT.md", {
    x: 0.7, y: 7.02, w: 11.9, h: 0.32, margin: 0,
    fontFace: "Arial", fontSize: 10, color: GRAY,
  });

  s.addNotes("벤치마크 설명: 같은 녹음을 자동 파이프라인과 별도 수동 정밀 판독으로 이중 분석해 비교 — 핵심 결론 일치, 자동이 4건을 추가 발견(녹음 고지→발화 위축 상관 등). 결정 3건 중 3번이 가장 급함: 전용 노트북 셋업 전에 계정 방침이 필요.");
}

pres.writeFile({ fileName: "FieldVoice_추진보고_20260820.pptx" }).then(() => {
  console.log("생성 완료: FieldVoice_추진보고_20260820.pptx");
});
