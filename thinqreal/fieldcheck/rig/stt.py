#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
#  L2 내용 판정 — 로컬 STT (구축 2단계)
#
#  L1(응답 유무·지연)만으로는 "말은 했는데 엉뚱한 답"을 잡을 수 없다.
#  녹음을 로컬에서 텍스트로 바꾼 뒤 기대/금지 키워드로 내용을 판정한다.
#
#  - 클라우드 STT를 쓰지 않는 이유: 공간 음성이 외부로 나가지 않도록
#    (보안) + 사용량 과금 없음 + 사외망 단절 시에도 판정 가능
#  - 엔진: faster-whisper 우선(CPU에서 수배 빠름), 없으면 openai-whisper
#  - 둘 다 없으면 L2는 조용히 건너뛴다 → 1단계(L1)는 그대로 동작
#
#  설치 (둘 중 하나):
#    pip install faster-whisper      (권장)
#    pip install openai-whisper
# ============================================================

import re

import numpy as np

_MODEL = None
_ENGINE = None
_LOAD_FAILED = False
_LOAD_ERROR = None      # 엔진은 있는데 모델 로딩만 실패한 경우의 사유

# ThinQ ON이 "듣긴 했으나 제대로 답하지 못했을 때" 내는 상투적 표현.
# 여기에 걸리면 소리가 났더라도 내용 판정은 실패로 본다.
DEFAULT_FORBID = [
    '모르겠', '죄송', '다시 말씀', '이해하지 못', '이해할 수 없',
    '지원하지 않', '확인할 수 없', '알 수 없',
]

_PUNCT = re.compile(r'[\s.,!?~…"\'’“”·\-—()\[\]]+')


def normalize(text):
    """공백·문장부호를 없애고 소문자화 — 키워드 포함 검사를 안정적으로."""
    return _PUNCT.sub('', str(text or '')).lower()


# ── 엔진 로딩 ───────────────────────────────────────────────

def available(cfg):
    return bool((cfg.get('stt') or {}).get('enabled', True))


def load_model(cfg, verbose=True):
    """STT 모델을 한 번만 읽어 재사용. 사용할 수 없으면 (None, None)."""
    global _MODEL, _ENGINE, _LOAD_FAILED, _LOAD_ERROR
    if _MODEL is not None or _LOAD_FAILED:
        return _MODEL, _ENGINE

    opt = cfg.get('stt') or {}
    size = opt.get('model', 'small')
    want = str(opt.get('engine', 'auto')).lower()
    installed = False

    if want in ('auto', 'faster-whisper'):
        try:
            from faster_whisper import WhisperModel
            installed = True
            if verbose:
                print(f'  STT 모델 준비 중... (faster-whisper / {size}) — 최초 1회는 내려받느라 몇 분 걸립니다')
            _MODEL = WhisperModel(size, device='cpu', compute_type='int8')
            _ENGINE = 'faster-whisper'
            return _MODEL, _ENGINE
        except ImportError:
            pass
        except Exception as e:
            _LOAD_ERROR = f'faster-whisper: {e}'
            print(f'  [주의] faster-whisper 로딩 실패: {e}')

    if want in ('auto', 'whisper', 'openai-whisper'):
        try:
            import whisper
            installed = True
            if verbose:
                print(f'  STT 모델 준비 중... (openai-whisper / {size}) — 최초 1회는 내려받느라 몇 분 걸립니다')
            _MODEL = whisper.load_model(size)
            _ENGINE = 'openai-whisper'
            return _MODEL, _ENGINE
        except ImportError:
            pass
        except Exception as e:
            _LOAD_ERROR = f'openai-whisper: {e}'
            print(f'  [주의] openai-whisper 로딩 실패: {e}')

    _LOAD_FAILED = True
    if installed:
        # 엔진은 깔려 있는데 모델을 못 읽은 경우 — 대개 첫 실행 시 모델 파일을
        # 내려받지 못한 상황(사외망 차단·오프라인)이다. 재설치는 해결책이 아니다.
        print('  [주의] STT 엔진은 설치되어 있으나 모델을 읽지 못해 L2(내용 판정)를 건너뜁니다.')
        print(f'         사유: {_LOAD_ERROR}')
        print('         모델 파일은 첫 실행 때 인터넷에서 내려받습니다. 인터넷이 되는 곳에서')
        print(f'         한 번 실행해 캐시를 만든 뒤 리그에 옮기거나, stt.model을 더 작은 값'
              f'(현재 "{size}" → "base"/"tiny")으로 바꿔 보세요.')
    else:
        print('  [주의] STT 엔진이 없어 L2(내용 판정)를 건너뜁니다. 설치:  pip install faster-whisper')
    return None, None


# ── 음성 → 텍스트 ───────────────────────────────────────────

def _to_float32_16k(samples, samplerate):
    x = np.asarray(samples).astype(np.float32) / 32768.0
    if samplerate != 16000:      # Whisper 계열은 16kHz 입력을 전제로 한다
        n = int(round(len(x) * 16000 / samplerate))
        x = np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype(np.float32)
    return x


def transcribe(samples, samplerate, cfg, verbose=True):
    """녹음을 텍스트로. 엔진이 없거나 실패하면 None.

    vocabulary_hint(initial_prompt): Whisper에게 "이런 말이 나올 것"이라고
    미리 알려주는 어휘 힌트. 지명(등촌동·마곡)이나 제품명(ThinQ ON)처럼
    일반 한국어 모델이 자주 틀리는 고유명사의 인식률을 올린다.
    별도의 AI 엔진 연동 없이 정확도를 개선하는 가장 값싼 방법.
    """
    model, engine = load_model(cfg, verbose)
    if model is None:
        return None

    opt = cfg.get('stt') or {}
    lang = opt.get('language', 'ko')
    hint = opt.get('vocabulary_hint') or None
    audio = _to_float32_16k(samples, samplerate)
    try:
        if engine == 'faster-whisper':
            segments, _ = model.transcribe(audio, language=lang, beam_size=1,
                                           vad_filter=True, initial_prompt=hint)
            return ''.join(s.text for s in segments).strip()
        result = model.transcribe(audio, language=lang, fp16=False,
                                  initial_prompt=hint)
        return str(result.get('text', '')).strip()
    except Exception as e:
        print(f'  [주의] STT 변환 실패: {e}')
        return None


# ── 내용 판정 ───────────────────────────────────────────────

def judge(text, scenario, cfg):
    """텍스트가 시나리오의 기대에 맞는지 판정.

    - forbid_any: 하나라도 있으면 실패 ("잘 모르겠어요" 류 — 말은 했지만
      알아듣지 못한 상태. L1으로는 절대 못 잡는 실패이자 L2의 핵심 가치)
    - expect_all: 전부 있어야 통과
    - expect_any: 하나 이상 있어야 통과
    - 기대 키워드가 없는 시나리오(자유 대화)는 최소 길이만 본다
      — 생성형 답변은 내용이 매번 달라 키워드 고정이 불가능하기 때문

    반환: {'passed': bool, 'reason': str, 'expected': str}
    """
    opt = cfg.get('stt') or {}
    norm = normalize(text)
    min_chars = int(opt.get('min_chars', 4))

    forbid = scenario.get('forbid_any')
    if forbid is None:
        forbid = opt.get('forbid_any_default', DEFAULT_FORBID)
    expect_any = scenario.get('expect_any') or []
    expect_all = scenario.get('expect_all') or []

    expected = ' / '.join(filter(None, [
        ('any: ' + ','.join(expect_any)) if expect_any else '',
        ('all: ' + ','.join(expect_all)) if expect_all else '',
        f'최소 {min_chars}자' if not (expect_any or expect_all) else '',
    ]))

    if not norm:
        return {'passed': False, 'reason': '인식된 말이 없음 (녹음은 되었으나 텍스트 변환 결과가 비어 있음)',
                'expected': expected}

    for w in forbid:
        if normalize(w) in norm:
            return {'passed': False, 'reason': f'회피 표현 감지: "{w}" — 질문을 알아듣지 못한 응답',
                    'expected': expected}

    missing = [w for w in expect_all if normalize(w) not in norm]
    if missing:
        return {'passed': False, 'reason': f'필수 키워드 누락: {", ".join(missing)}', 'expected': expected}

    if expect_any:
        hit = [w for w in expect_any if normalize(w) in norm]
        if not hit:
            return {'passed': False, 'reason': f'기대 키워드 없음 (기대: {", ".join(expect_any)})',
                    'expected': expected}
        return {'passed': True, 'reason': f'키워드 일치: {", ".join(hit)}', 'expected': expected}

    if expect_all:
        return {'passed': True, 'reason': '필수 키워드 모두 포함', 'expected': expected}

    if len(norm) < min_chars:
        return {'passed': False, 'reason': f'응답이 너무 짧음 ({len(norm)}자 < {min_chars}자)',
                'expected': expected}
    return {'passed': True, 'reason': f'자유 응답 {len(norm)}자', 'expected': expected}
