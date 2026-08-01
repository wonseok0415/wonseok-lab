#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
#  예약 슬롯 회피 (구축 2단계)
#
#  점검 장비는 ThinQ Real 공간에서 실제로 "소리를 내어" 말을 건다.
#  방문객 시연 중에 점검 발화가 나가면 시연을 방해하므로, 발화 전에
#  예약 관리 시스템에 오늘 예약 현황을 물어보고 예약 시간대에는
#  점검을 건너뛴다.
#
#  조회: GET {endpoint_url}?type=availability&date=YYYY-MM-DD
#        → { bookedSlots:[1,3], pendingCounts:{...}, blockedSlots:[2] }
#
#  ※ 사내 이관 대비 (DESIGN.md §10): 조회 주소는 config의 endpoint_url을
#    그대로 재사용하고, 슬롯 시간표도 config에 두어 코드 수정 없이 바꿀 수
#    있게 한다.
# ============================================================

import datetime
import json
import urllib.parse
import urllib.request

# 예약 슬롯 기본 시간표 (CLAUDE.md의 확정 슬롯 — config로 덮어쓸 수 있음)
DEFAULT_SLOT_WINDOWS = {
    '1': '09:00-10:30',
    '2': '13:00-14:30',
    '3': '15:00-16:30',
}


def _parse_hhmm(s):
    h, m = s.split(':')
    return datetime.time(int(h), int(m))


def slot_windows(cfg):
    """{슬롯번호(int): (시작 time, 종료 time)} 반환."""
    raw = (cfg.get('booking_avoidance') or {}).get('slot_windows') or DEFAULT_SLOT_WINDOWS
    out = {}
    for k, v in raw.items():
        try:
            start_s, end_s = str(v).split('-')
            out[int(k)] = (_parse_hhmm(start_s.strip()), _parse_hhmm(end_s.strip()))
        except (ValueError, AttributeError):
            print(f'  [주의] slot_windows 형식 오류(슬롯 {k}: {v}) — "09:00-10:30" 형태여야 합니다. 무시합니다.')
    return out


def fetch_availability(cfg, date_str, timeout=20):
    """예약 시스템에서 해당 날짜의 마감/차단 슬롯을 조회. 실패 시 None."""
    url = cfg.get('endpoint_url', '')
    if not url or 'script.google.com' not in url:
        return None
    q = urllib.parse.urlencode({'type': 'availability', 'date': date_str})
    try:
        with urllib.request.urlopen(f'{url}?{q}', timeout=timeout) as resp:
            body = json.loads(resp.read().decode('utf-8'))
    except Exception as e:      # 네트워크 단절 등 — 판단은 호출부(캐시/스킵)에 맡긴다
        print(f'  [주의] 예약 현황 조회 실패: {e}')
        return None
    if not isinstance(body, dict) or 'bookedSlots' not in body:
        print(f'  [주의] 예약 현황 응답 형식이 예상과 다릅니다: {body}')
        return None
    return body


def busy_slots(cfg, avail):
    """회피 대상 슬롯 번호 집합. (확정 / 관리자 차단 / 선택적으로 대기중)"""
    opt = cfg.get('booking_avoidance') or {}
    slots = set(int(s) for s in (avail.get('bookedSlots') or []))
    if opt.get('avoid_blocked', True):
        slots |= set(int(s) for s in (avail.get('blockedSlots') or []))
    if opt.get('avoid_pending', False):
        slots |= set(int(s) for s in (avail.get('pendingCounts') or {}).keys())
    return slots


def blocking_slot(cfg, avail, now):
    """지금이 회피 대상 슬롯(전후 여유 포함) 안이면 (슬롯번호, 시작, 종료) 반환, 아니면 None."""
    opt = cfg.get('booking_avoidance') or {}
    before = datetime.timedelta(minutes=float(opt.get('guard_before_minutes', 20)))
    after = datetime.timedelta(minutes=float(opt.get('guard_after_minutes', 10)))
    windows = slot_windows(cfg)

    for slot in sorted(busy_slots(cfg, avail)):
        if slot not in windows:
            continue
        start_t, end_t = windows[slot]
        start = datetime.datetime.combine(now.date(), start_t) - before
        end = datetime.datetime.combine(now.date(), end_t) + after
        if start <= now <= end:
            return slot, start, end
    return None


def check(cfg, state, now=None):
    """지금 점검 발화를 해도 되는지 판단.

    반환: (허용 여부, 사유 문자열)

    조회에 실패하면 같은 날짜의 마지막 성공 응답(state의 캐시)을 대신 쓴다.
    캐시도 없으면 on_query_failure 설정에 따르는데, 기본값은 'skip' —
    "예약이 있는지 모르는 상태"에서 스피커로 말을 거는 위험(시연 방해)이
    한 회차 점검을 거르는 손실보다 크기 때문이다.
    """
    opt = cfg.get('booking_avoidance') or {}
    if not opt.get('enabled', True):
        return True, '예약 회피 비활성(booking_avoidance.enabled=false)'

    now = now or datetime.datetime.now()
    date_str = now.strftime('%Y-%m-%d')

    avail = fetch_availability(cfg, date_str)
    source = '조회'
    if avail is not None:
        state['availability_cache'] = {'date': date_str, 'data': avail,
                                       'fetched_at': now.isoformat(timespec='seconds')}
    else:
        cache = state.get('availability_cache') or {}
        if cache.get('date') == date_str and cache.get('data'):
            avail = cache['data']
            source = f"캐시({cache.get('fetched_at', '?')})"
        else:
            if str(opt.get('on_query_failure', 'skip')).lower() == 'proceed':
                return True, '예약 현황을 확인하지 못했으나 설정에 따라 점검 진행(on_query_failure=proceed)'
            return False, '예약 현황을 확인하지 못해 점검을 건너뜁니다 (시연 중 발화 방지). 네트워크를 확인해 주세요'

    hit = blocking_slot(cfg, avail, now)
    if hit:
        slot, start, end = hit
        return False, (f'{slot}회차 예약 시간대({start.strftime("%H:%M")}~{end.strftime("%H:%M")}, '
                       f'전후 여유 포함) — 시연 방해 방지를 위해 건너뜁니다 [{source}]')

    booked = sorted(busy_slots(cfg, avail))
    detail = f'오늘 회피 대상 회차: {booked}' if booked else '오늘 예약 없음'
    return True, f'{detail} [{source}]'
