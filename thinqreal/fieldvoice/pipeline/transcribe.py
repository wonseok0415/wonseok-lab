"""FieldVoice 전사 단계 — 로컬 faster-whisper로 오디오를 타임스탬프 있는 텍스트로.

FieldCheck rig/stt.py의 검증된 접근을 이식: 로컬 실행(음성이 장비 밖으로 안 나감),
어휘 힌트로 고유명사 오인식 완화. 엔진 미설치 시 명확한 안내와 함께 실패한다
(전사 .txt 파일을 직접 입력하는 우회로가 파이프라인에 있음).
"""

AUDIO_EXTS = {".wav", ".mp3", ".m4a", ".mp4", ".aac", ".flac", ".ogg", ".webm"}


def _fmt_ts(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int(seconds % 3600 // 60)
    s = int(seconds % 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def transcribe(audio_path, cfg, progress=None) -> str:
    """오디오 파일 → "[MM:SS] 발화" 줄들의 텍스트. progress(detail_str) 콜백 선택."""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise RuntimeError(
            "faster-whisper가 설치되어 있지 않습니다. 오디오 전사를 하려면:\n"
            "  venv/bin/pip install faster-whisper\n"
            "설치가 어려우면 전사 텍스트(.txt) 파일을 대신 업로드하세요 (전사 단계를 건너뜁니다)."
        )

    model_name = cfg.get("whisper_model", "small")
    if progress:
        progress(f"Whisper 모델({model_name}) 로딩 중 — 첫 실행은 다운로드로 수 분 걸릴 수 있음")
    model = WhisperModel(model_name, device="auto", compute_type="auto")

    segments, info = model.transcribe(
        str(audio_path),
        language=cfg.get("whisper_language", "ko"),
        initial_prompt=cfg.get("vocabulary_hint", ""),
        vad_filter=True,
        # 무음·기계 소음 구간에서 같은 문장을 수십 번 반복하는 환청 루프 완화
        # (첫 실녹음 실측: 동일 단어 40줄 연속 — 판독 리포트 §7)
        condition_on_previous_text=cfg.get("whisper_condition_on_previous_text", False),
    )

    entries = []
    for seg in segments:  # 제너레이터 — 순회하면서 실제 전사가 진행됨
        text = seg.text.strip()
        if not text:
            continue
        entries.append((seg.start, text))
        if progress and len(entries) % 20 == 0:
            progress(f"전사 진행 중 — {_fmt_ts(seg.end)} 지점 ({len(entries)}개 발화)")

    if not entries:
        raise RuntimeError("전사 결과가 비어 있습니다 — 무음 파일이거나 포맷 문제일 수 있습니다.")
    return "\n".join(_collapse_repeats(entries))


def _collapse_repeats(entries, threshold=3):
    """연속 동일 발화(환청 루프)를 1줄 + 반복 표기로 압축. threshold회 미만 반복은 그대로 둔다."""
    lines = []
    i = 0
    while i < len(entries):
        start, text = entries[i]
        j = i + 1
        while j < len(entries) and entries[j][1] == text:
            j += 1
        count = j - i
        lines.append(f"[{_fmt_ts(start)}] {text}")
        if count >= threshold:
            lines.append(
                f"(위 발화가 {_fmt_ts(entries[j - 1][0])}까지 {count}회 반복됨 — STT 환청 의심 구간, 내용 아님)"
            )
        elif count > 1:
            for k in range(i + 1, j):
                lines.append(f"[{_fmt_ts(entries[k][0])}] {entries[k][1]}")
        i = j
    return lines
