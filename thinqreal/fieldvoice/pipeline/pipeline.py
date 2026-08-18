#!/usr/bin/env python3
"""FieldVoice 파이프라인 오케스트레이터.

녹취 입력(오디오 또는 전사 .txt) → 전사 → 화자 라벨링 → 요약 → 맥락 분석
→ 인사이트 도출 → output/<세션>/에 단계별 마크다운 + 통합 report.md 저장.

사용:  python pipeline.py <오디오|전사.txt> [--name 세션이름]
웹 UI는 webapp.py (run.sh로 기동) — 같은 run_pipeline()을 호출한다.
"""
import argparse
import datetime
import json
import re
import sys
from pathlib import Path

import agents
import transcribe as stt

BASE = Path(__file__).resolve().parent
OUTPUT_ROOT = BASE / "output"

STAGES = [
    ("transcribe", "전사"),
    ("label", "화자 라벨링"),
    ("summary", "요약"),
    ("context", "맥락 분석"),
    ("insight", "인사이트 도출"),
    ("save", "파일 저장"),
]


def load_config():
    cfg = json.loads((BASE / "config.example.json").read_text(encoding="utf-8"))
    local = BASE / "config.json"
    if local.exists():
        cfg.update(json.loads(local.read_text(encoding="utf-8")))
    return cfg


def _session_id(input_path: Path, name: str | None) -> str:
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    label = name or input_path.stem
    label = re.sub(r"[^\w가-힣-]+", "_", label)[:40] or "session"
    return f"{stamp}_{label}"


def run_pipeline(input_path, name=None, progress=None, cfg=None):
    """전체 파이프라인 실행. progress(stage_key, status, detail) 콜백으로 UI에 상태 전달.
    status: running | done | skipped | error. 반환: 세션 출력 폴더 Path."""
    cfg = cfg or load_config()
    input_path = Path(input_path)

    def report(stage, status, detail=""):
        if progress:
            progress(stage, status, detail)

    sid = _session_id(input_path, name)
    outdir = OUTPUT_ROOT / sid
    outdir.mkdir(parents=True, exist_ok=True)

    def save(fname, text):
        (outdir / fname).write_text(text, encoding="utf-8")

    # 1) 전사 (텍스트 입력이면 건너뜀)
    if input_path.suffix.lower() in stt.AUDIO_EXTS:
        report("transcribe", "running", "로컬 Whisper 전사")
        raw = stt.transcribe(input_path, cfg, progress=lambda d: report("transcribe", "running", d))
        report("transcribe", "done", f"{len(raw.splitlines())}개 발화")
    else:
        raw = input_path.read_text(encoding="utf-8")
        report("transcribe", "skipped", "전사 텍스트 직접 입력 — STT 건너뜀")
    save("01_transcript.md", f"# 원본 전사\n\n```\n{raw}\n```\n")

    # 2) 화자 라벨링
    report("label", "running", "1채널 전사에 화자 라벨 부여")
    labeled = agents.label_speakers(raw, cfg)
    save("02_labeled.md", labeled)
    report("label", "done")

    # 3) 요약
    report("summary", "running")
    summary = agents.summarize(labeled, cfg)
    save("03_summary.md", summary)
    report("summary", "done")

    # 4) 맥락 분석
    report("context", "running", "질문 프레임 매핑 + 자유 발화 하이라이트")
    context = agents.analyze_context(labeled, cfg)
    save("04_context.md", context)
    report("context", "done")

    # 5) 인사이트 도출
    report("insight", "running", "카테고리별 인사이트 + 개선 제안")
    insights = agents.extract_insights(labeled, summary, context, cfg)
    save("05_insights.md", insights)
    report("insight", "done")

    # 6) 통합 리포트 + 매니페스트
    report("save", "running")
    head = (
        f"# FieldVoice 세션 리포트 — {sid}\n\n"
        f"- 입력: `{input_path.name}` / 분석 모델: `{cfg.get('model')}`\n"
        f"- 생성: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        f"- ⚠ 개인정보: 이 리포트와 전사는 로컬 전용 — 저장소·공유 채널에 올리기 전 가명화 확인 (DESIGN.md §5)\n\n---\n\n"
    )
    save("report.md", head + insights + "\n\n---\n\n" + summary + "\n\n---\n\n" + context)
    manifest = {
        "id": sid,
        "source": input_path.name,
        "created": datetime.datetime.now().isoformat(timespec="seconds"),
        "model": cfg.get("model"),
        "files": ["report.md", "01_transcript.md", "02_labeled.md", "03_summary.md",
                  "04_context.md", "05_insights.md"],
    }
    save("session.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    report("save", "done", str(outdir))
    return outdir


def main():
    ap = argparse.ArgumentParser(description="FieldVoice 인터뷰 분석 파이프라인")
    ap.add_argument("input", help="오디오 파일 또는 전사 .txt")
    ap.add_argument("--name", help="세션 이름 (기본: 파일명)")
    args = ap.parse_args()

    labels = dict(STAGES)

    def progress(stage, status, detail=""):
        mark = {"running": "…", "done": "✓", "skipped": "―", "error": "✗"}.get(status, "?")
        print(f"[{mark}] {labels.get(stage, stage)}" + (f" — {detail}" if detail else ""), flush=True)

    try:
        outdir = run_pipeline(args.input, name=args.name, progress=progress)
    except Exception as e:
        print(f"\n실패: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"\n완료 — 결과: {outdir}/report.md")


if __name__ == "__main__":
    main()
