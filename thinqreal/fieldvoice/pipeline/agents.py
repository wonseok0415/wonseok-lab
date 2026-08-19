"""FieldVoice LLM 에이전트 계층 — 화자 라벨링 / 요약 / 맥락 분석 / 인사이트 도출.

Whisper는 전사만 담당하고(transcribe.py), 이 파일의 에이전트들이 그 위의 분석을
담당한다 (DESIGN.md §4 역할 분담). 분석 백엔드는 둘 중 하나 (README §2):

- claude_cli: Claude Code CLI 헤드리스(-p) 호출 — **구독 사용량으로 처리, API 크레딧 불필요**
- api: Claude API 직접 호출(claude-opus-5, 스트리밍+적응형 사고+안전 폴백) — 크레딧 과금

기본(auto)은 API 자격 증명이 있으면 api, 없고 claude 명령이 있으면 claude_cli.
"""
import os
import shutil
import subprocess
import tempfile

import anthropic

_client = None


def _resolve_backend(cfg):
    choice = cfg.get("llm_backend", "auto")
    if choice in ("api", "claude_cli"):
        return choice
    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        return "api"
    if shutil.which("claude"):
        return "claude_cli"
    raise RuntimeError(
        "분석 백엔드가 없습니다 — Claude Code CLI 설치(구독 활용, 크레딧 불필요) 또는 "
        "ANTHROPIC_API_KEY 설정 중 하나가 필요합니다 (README §2)."
    )


def _get_client():
    global _client
    if _client is None:
        try:
            _client = anthropic.Anthropic()  # env 키 또는 ant 프로필 자동 해석
        except Exception:
            raise RuntimeError(
                "Claude API 인증 정보를 찾지 못했습니다 — ANTHROPIC_API_KEY 환경변수를 "
                "설정하거나 `ant auth login`을 실행하세요 (README §2)."
            )
    return _client


# ── 공통 배경 (모든 에이전트의 시스템 프롬프트 첫 블록 — 프롬프트 캐시 대상) ──

BACKGROUND = """당신은 FieldVoice의 분석 엔진이다. FieldVoice는 LG ThinQ Real(마곡 사이언스파크의
30평형 AI홈 연구·쇼룸)의 방문 인터뷰를 분석해 인사이트를 도출하는 시스템이다.

상황: 도슨트(안내자, LG 직원)가 방문객에게 쇼룸(거실·주방·침실·런드레스룸·욕실·현관)을
안내하며 시연 중간중간 설계된 질문을 던진다. 녹음은 1채널(모노)이라 화자 정보가 없다.

도슨트의 질문 프레임 (유형 → 대표 질문):
- 로망: "영화나 드라마에서 '저 집에서 살아보고 싶다' 했던 장면 있으세요?"
- 부러움: "집이나 사는 모습으로 제일 부러운 사람은? 뭐가 부러우셨어요?"
- 아쉬움의 순간: "오늘 아침 집 나오면서 '집이 이 정도는 알아서 해줬으면' 싶었던 순간은?"
- 경계: "집이 먼저 알아서 움직이는 것 — '챙겨준다'와 '지켜본다'는 느낌은 어디서 갈릴까요?"
- 미래 일기: "3년 뒤 어느 저녁 일기에 '집' 얘기가 한 문장 나온다면?"
- 삶(루틴): 아침 기상 루틴, 요리, 집안일 위임 등 생활 질문

질문 설계 원칙 (분석 시 판단 기준): '왜'를 직접 물으면 지어낸 답이 나온다.
제품이 아니라 삶을 물어야 하고, 로망·부러움이 가치관과 욕망을 드러낸다.
의도한 질문의 답 밖에서 나온 자유 발화가 1급 데이터다.

인사이트 카테고리 (질문 유형과 매핑):
1. 가치관·욕망 (← 로망·부러움)
2. 페인포인트/JTBD (← 아쉬움·삶)
3. 신뢰·프라이버시 수용선 (← 경계)
4. 기대와 잔상 (← 미래 일기·클로징 반응)

모든 출력은 한국어 마크다운으로 작성한다. 근거 없는 단정 대신 전사 인용을 근거로 남긴다.

전사 유의사항: "(위 발화가 …회 반복됨 — STT 환청 의심 구간)" 표기는 전사 엔진의 잡음
아티팩트다 — 대화 내용으로 취급하지 말고, 해당 구간은 기계음·무음 구간이었다고만 참고한다.
고유명사 오인식이 흔하다(예: ThinQ ON이 신큐온·싱크온 등으로 적힘) — 문맥으로 보정해 읽는다."""


def _call(system_blocks, user_text, cfg, max_tokens=64000):
    """공통 호출부 — 설정된 백엔드로 라우팅."""
    if _resolve_backend(cfg) == "claude_cli":
        return _call_claude_cli(system_blocks, user_text, cfg)
    return _call_api(system_blocks, user_text, cfg, max_tokens)


def _call_claude_cli(system_blocks, user_text, cfg):
    """Claude Code CLI 헤드리스(-p) 호출 — 구독 사용량으로 처리되어 API 크레딧 불필요.

    cwd를 저장소 밖(임시 폴더)으로 두어 CLAUDE.md 등 프로젝트 컨텍스트가
    분석 프롬프트에 섞이지 않게 한다.
    """
    prompt = "\n\n".join([b["text"] for b in system_blocks] + ["---", user_text])
    cmd = ["claude", "-p", "--output-format", "text"]
    model = cfg.get("claude_cli_model", "")
    if model:
        cmd += ["--model", model]
    try:
        res = subprocess.run(
            cmd, input=prompt, capture_output=True, text=True,
            timeout=int(cfg.get("claude_cli_timeout_sec", 1800)),
            cwd=tempfile.gettempdir(),
        )
    except FileNotFoundError:
        raise RuntimeError("claude 명령을 찾을 수 없습니다 — Claude Code CLI 설치가 필요합니다 (README §2).")
    except subprocess.TimeoutExpired:
        raise RuntimeError("Claude CLI 응답 시간 초과 — 잠시 후 다시 시도하세요.")
    if res.returncode != 0:
        err = (res.stderr or res.stdout or "").strip()
        raise RuntimeError(
            f"Claude CLI 오류: {err[:300] or '원인 미상'} — 터미널에서 `claude` 단독 실행으로 로그인 상태를 확인하세요."
        )
    out = res.stdout.strip()
    if not out:
        raise RuntimeError("Claude CLI가 빈 응답을 반환했습니다 — 다시 시도하세요.")
    return out


def _call_api(system_blocks, user_text, cfg, max_tokens=64000):
    """Claude API 직접 호출 — 스트리밍으로 긴 입출력 안전, stop_reason 검사 포함."""
    client = _get_client()
    try:
        with client.beta.messages.stream(
            model=cfg.get("model", "claude-opus-5"),
            max_tokens=max_tokens,
            thinking={"type": "adaptive"},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",  # 안전 분류기 거절 시 서버가 대체 모델로 이어서 처리
            system=system_blocks,
            messages=[{"role": "user", "content": user_text}],
        ) as stream:
            msg = stream.get_final_message()
    except anthropic.AuthenticationError:
        raise RuntimeError(
            "Claude API 인증 실패 — ANTHROPIC_API_KEY 환경변수 또는 `ant auth login`을 확인하세요 (README §2)."
        )
    except anthropic.RateLimitError:
        raise RuntimeError("Claude API 사용량 한도 초과 — 잠시 후 다시 시도하세요.")
    except anthropic.APIStatusError as e:
        raise RuntimeError(f"Claude API 오류 (HTTP {e.status_code}): {e.message}")
    except anthropic.APIConnectionError:
        raise RuntimeError("Claude API 연결 실패 — 네트워크(프록시/방화벽)를 확인하세요.")
    except Exception as e:
        if "authentication method" in str(e):  # SDK가 요청 시점에 던지는 자격 증명 부재 오류
            raise RuntimeError(
                "Claude API 인증 정보가 없습니다 — ANTHROPIC_API_KEY 환경변수를 설정하거나 "
                "`ant auth login`을 실행한 뒤 run.sh를 다시 시작하세요 (README §2)."
            )
        raise

    if msg.stop_reason == "refusal":
        detail = getattr(msg.stop_details, "explanation", "") if msg.stop_details else ""
        raise RuntimeError(f"모델이 요청을 거절했습니다: {detail or '사유 미제공'}")

    text = "".join(b.text for b in msg.content if b.type == "text")
    if msg.stop_reason == "max_tokens":
        text += "\n\n> ⚠ 출력이 길이 한도에서 잘렸습니다 — 결과가 불완전할 수 있습니다."
    return text


def _bg_block():
    return {"type": "text", "text": BACKGROUND, "cache_control": {"type": "ephemeral"}}


def _shared_system(labeled_transcript):
    """요약·맥락·인사이트 3단계가 같은 프리픽스를 쓰도록 구성 — 프롬프트 캐시로
    전사 전문을 한 번만 과금하고 이후 단계는 캐시에서 읽는다."""
    return [
        _bg_block(),
        {
            "type": "text",
            "text": "다음은 화자 라벨링이 끝난 인터뷰 전사 전문이다.\n\n" + labeled_transcript,
            "cache_control": {"type": "ephemeral"},
        },
    ]


# ── 에이전트 1: 화자 라벨링 (1채널 녹음 → 내용 기반 화자 구분) ──

def label_speakers(raw_transcript, cfg):
    system = [
        _bg_block(),
        {
            "type": "text",
            "text": """임무: 화자 정보가 없는 1채널 전사에 화자 라벨을 붙여라.

규칙:
- 도슨트는 안내·시연 멘트와 질문 프레임의 질문을 던지는 쪽이다. 방문객은 답하는 쪽이다.
- 각 발화 줄을 `**도슨트:**` / `**방문객:**` 접두어로 다시 쓴다.
- **그룹 투어(방문객 여러 명) 세션에서는 개별 방문객 구분을 시도하지 않는다** — 1채널
  전사에서 개별 구분은 오라벨 위험이 크므로 기본은 도슨트/방문객 2-way 라벨이다.
  내용상 확실히 구분되는 경우에만 `**방문객A:**`, `**방문객B:**`를 쓴다.
- 타임스탬프가 있으면 그대로 보존한다. 발화 내용은 절대 바꾸지 않는다(요약·수정 금지).
- 화자가 정말 불확실한 줄은 `**?:**`로 남긴다 (억지 배정 금지).
- 출력 맨 앞에 `## 화자 구성 추정` 섹션으로 몇 명이 참여했고 판단 근거가 무엇인지 3줄
  이내로 쓰고, 이어서 `## 라벨링된 전사` 아래 전문을 쓴다.""",
        },
    ]
    return _call(system, raw_transcript, cfg)


# ── 에이전트 2: 요약 ──

def summarize(labeled_transcript, cfg):
    user = """이 인터뷰를 다음 구성으로 요약하라:

## 세션 개요
(추정 길이·참여 인원·방문 목적 추정·전체 분위기 — 5줄 이내)

## 주제 타임라인
(시간순으로 어떤 공간/주제를 지났는지, 타임스탬프 구간과 함께)

## 핵심 문답 5선
(가장 정보량 많은 질문-답변 쌍 5개 — 질문 유형 태그와 함께, 답변은 요지+짧은 직접 인용)

## 전사 품질 메모
(오인식 의심 구간, 끊긴 구간, 화자 라벨 불확실 구간 — 분석 신뢰도에 영향 주는 것만)"""
    return _call(_shared_system(labeled_transcript), user, cfg)


# ── 에이전트 3: 맥락 분석 ──

def analyze_context(labeled_transcript, cfg):
    user = """이 인터뷰를 다음 구성으로 맥락 분석하라:

## 질문 프레임 매핑
(프레임의 6개 질문 유형별로: 실제로 던져진 질문 → 답변 요지 → 직접 인용. 안 던져진
유형은 "미사용"으로 명시 — 다음 인터뷰 개선 자료가 된다)

## 자유 발화 하이라이트 ★
(질문과 무관하게 방문객이 스스로 꺼낸 말 — 이 시스템의 1급 데이터다. 발언 인용 +
타임스탬프 + 왜 주목할 만한지 한 줄. 최소 3개, 없으면 "없음"과 그 이유)

## 반응 신호
(감탄·웃음·머뭇거림·짧아진 대답·화제 회피가 나타난 지점과 그 직전에 무엇이 있었는지)

## 도슨트 질문 운영 점검
(안티패턴 사용 지점: '왜' 직접 질문, 단도직입 구매 의향 질문, 유도 질문. 잘 된 질문도
1개 이상 짚기 — 질문 프레임 개선 루프의 입력이다)

## 검증된 설명 프레임 채집
(도슨트가 "반응이 좋았다/효과 좋았다/제일 잘 통했다"고 스스로 보고하는 비유·설명 방식
— 예: 영화·캐릭터·드라마 비유 — 이 있으면 별도 기록하라. 현장에서 이미 검증된 로망
원형이므로 질문 프레임·시연 멘트 개선의 1급 재료다. 없으면 "없음")"""
    return _call(_shared_system(labeled_transcript), user, cfg)


# ── 에이전트 4: 인사이트 도출 ──

def extract_insights(labeled_transcript, summary_md, context_md, cfg):
    user = f"""앞서 다른 에이전트가 작성한 요약과 맥락 분석이 아래에 있다. 전사 전문(시스템 프롬프트)과
함께 검토하여 최종 인사이트를 도출하라.

<요약>
{summary_md}
</요약>

<맥락_분석>
{context_md}
</맥락_분석>

출력 구성:

## 카테고리별 인사이트
4개 카테고리(가치관·욕망 / 페인포인트·JTBD / 신뢰·프라이버시 수용선 / 기대와 잔상)별로:
- 인사이트 문장 (한 줄, 단정형)
- 근거 인용 (전사에서 직접)
- 신뢰도: **확실**(직접 발화 근거) / **추정**(해석 개입)

## 시연·운영 개선 제안
(이 인터뷰가 시연 시나리오·공간 운영·질문 프레임에 시사하는 실행 가능한 제안 3~5개,
각각 근거 인사이트 표기)

## 다음 인터뷰 검증 가설
(이번엔 표본 1건 — 단정 대신 다음 방문에서 확인할 가설 2~3개와 그걸 검증할 질문 제안)

## 한 줄 결론
(이 세션에서 단 하나만 기억한다면)"""
    return _call(_shared_system(labeled_transcript), user, cfg)
