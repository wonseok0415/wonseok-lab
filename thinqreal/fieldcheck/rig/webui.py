#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
#  ThinQ ON 자동 점검 제어판 — 로컬 웹 UI (순수 추가 기능)
#
#  코드·명령줄을 건드리지 않고 브라우저에서 점검 장비를 조작·확인한다.
#  탭 구성:
#    · 현황   : 장비 상태(마이크/스피커/카메라)·설정 요약·조작 버튼·기록 열람
#    · 점검 음성: 점검에 쓰는 음성 파일 재생·재생성(TTS) — 기존 파일은 자동 백업
#    · 결과서 : 서버(운영 시트)에 기록된 점검 결과를 날짜별로 요약
#               (아침 요약 메일은 서버가 같은 기록으로 생성)
#
#  실행:  python webui.py     (브라우저가 자동으로 열림)
#  종료:  이 창을 닫거나 Ctrl+C
#
#  보안: 127.0.0.1 전용 — 같은 컴퓨터의 브라우저에서만 접속 가능하다.
#  기존 자동 점검(fieldcheck.py)에는 영향이 없다. 조작은 명령줄과 동일한
#  하위 프로세스 실행이라, UI로 하든 명령으로 하든 결과가 같다.
# ============================================================
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')
LOG_PATH = os.path.join(BASE_DIR, 'results.jsonl')
REC_DIR = os.path.join(BASE_DIR, 'recordings')
PHRASE_DIR = os.path.join(BASE_DIR, 'phrases')
PHRASE_BACKUP_DIR = os.path.join(PHRASE_DIR, 'backups')
SCHED_LOG = os.path.join(BASE_DIR, 'logs', 'schedule.log')
PORT = 8477

LEVEL_LABEL = {'L1': '응답 점검', 'L2': '내용 점검', 'L3': '동작 점검'}
SAFE_WAV = re.compile(r'^[A-Za-z0-9_\-]+\.wav$')

# 실행 중인 조작 (한 번에 하나 — 마이크·스피커·카메라는 공유 불가)
ACTION = {'running': False, 'label': '', 'output': '', 'lock': threading.Lock()}


def load_cfg():
    try:
        with open(CONFIG_PATH, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def camera_device(cfg):
    for s in (cfg or {}).get('scenarios', []):
        if 'camera' in s:
            return s['camera'].get('device', 0)
    return 0


def audio_status(cfg):
    """이름 지정 장치가 실제로 연결되어 있는지 확인 (fieldcheck의 해석기 재사용)."""
    out = {'input': None, 'output': None, 'note': ''}
    try:
        import sounddevice as sd
        import fieldcheck
        devices = sd.query_devices()
        probe = {'input_device': cfg.get('input_device'), 'output_device': cfg.get('output_device')}
        # resolve는 print를 하므로 조용히 실행
        import io, contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            fieldcheck.resolve_audio_devices(probe)
        for key, slot in (('input_device', 'input'), ('output_device', 'output')):
            spec = cfg.get(key)
            resolved = probe.get(key)
            if isinstance(resolved, int):
                out[slot] = {'spec': spec, 'index': resolved, 'name': devices[resolved]['name'], 'ok': True}
            elif spec:
                out[slot] = {'spec': spec, 'ok': False}
            else:
                out[slot] = {'spec': '기본 장치', 'ok': True}
    except Exception as e:
        out['note'] = f'오디오 장치 조회 실패: {e}'
    return out


def recent_results(limit=12):
    rows = []
    try:
        with open(LOG_PATH, encoding='utf-8') as f:
            lines = f.readlines()[-limit * 3:]
        for line in lines:
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            rows.append({
                'time': str(r.get('timestamp', ''))[:19].replace('T', ' '),
                'scenario': r.get('scenario_label', r.get('scenario_id', '')),
                'level': LEVEL_LABEL.get(r.get('level'), r.get('level', '')),
                'result': r.get('result', ''),
                'latency': r.get('latency_ms'),
                'note': r.get('note', ''),
            })
    except OSError:
        pass
    return rows[-limit:][::-1]


def sched_tail(lines=4):
    try:
        with open(SCHED_LOG, encoding='utf-8', errors='replace') as f:
            return ''.join(f.readlines()[-lines:]).strip()
    except OSError:
        return '(자동 실행 기록 없음 — 스케줄 등록 전이거나 아직 첫 실행 전)'


def list_recordings(limit=30):
    items = []
    for root, _dirs, files in os.walk(REC_DIR):
        for name in files:
            if name.startswith('.'):
                continue
            if not name.lower().endswith(('.wav', '.jpg', '.jpeg', '.png')):
                continue
            full = os.path.join(root, name)
            rel = os.path.relpath(full, REC_DIR).replace('\\', '/')
            try:
                st = os.stat(full)
            except OSError:
                continue
            items.append({'rel': rel, 'mtime': st.st_mtime,
                          'time': time.strftime('%m-%d %H:%M', time.localtime(st.st_mtime)),
                          'kind': 'audio' if name.lower().endswith('.wav') else 'image',
                          'size_kb': st.st_size // 1024})
    items.sort(key=lambda x: x['mtime'], reverse=True)
    return items[:limit]


def phrase_roles(cfg):
    """config 시나리오에서 각 음성 파일의 용도를 뽑는다: 파일명 → [용도, ...]"""
    roles = {}

    def add(path, role):
        if not path:
            return
        name = os.path.basename(str(path))
        roles.setdefault(name, [])
        if role not in roles[name]:
            roles[name].append(role)

    for s in (cfg or {}).get('scenarios', []):
        label = s.get('label', s.get('id', ''))
        add(s.get('wake_file'), '기동어')
        add(s.get('phrase_file'), f'명령 — {label}')
        add(s.get('confirm_file'), '확답')
    return roles


def list_phrases():
    cfg = load_cfg()
    roles = phrase_roles(cfg)
    items = []
    if os.path.isdir(PHRASE_DIR):
        for name in sorted(os.listdir(PHRASE_DIR)):
            full = os.path.join(PHRASE_DIR, name)
            # 맥에서 USB로 복사할 때 생기는 메타데이터 파일(._이름.wav 등 숨김
            # 파일)은 오디오가 아니므로 목록에서 제외
            if name.startswith('.'):
                continue
            if not (os.path.isfile(full) and name.lower().endswith('.wav')):
                continue
            st = os.stat(full)
            items.append({
                'name': name,
                'roles': roles.get(name, ['(미사용)']),
                'size_kb': st.st_size // 1024,
                'time': time.strftime('%Y-%m-%d %H:%M', time.localtime(st.st_mtime)),
            })
    # 사용 중인데 파일이 없는 것도 표시 (만들어야 할 파일)
    have = {i['name'] for i in items}
    for name, r in roles.items():
        if name not in have:
            items.append({'name': name, 'roles': r, 'size_kb': None, 'time': '(파일 없음)'})
    return items


def fetch_reports(days=7):
    """서버(운영 시트)의 점검 기록을 날짜별로 묶는다 — 요약 메일과 같은 원천."""
    cfg = load_cfg()
    url = (cfg or {}).get('endpoint_url', '')
    if 'script.google.com' not in url:
        return {'error': 'config.json의 endpoint_url이 없거나 올바르지 않습니다'}
    q = urllib.parse.urlencode({'type': 'health_checks', 'days': days})
    try:
        with urllib.request.urlopen(f'{url}?{q}', timeout=30) as resp:
            body = json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        return {'error': f'서버 조회 실패: {e}'}
    records = body.get('records', body if isinstance(body, list) else [])
    days_map = {}
    for r in records:
        ts = str(r.get('timestamp', ''))
        day = ts[:10]
        if not day:
            continue
        d = days_map.setdefault(day, {'date': day, 'total': 0, 'fail': 0, 'rows': []})
        d['total'] += 1
        if r.get('result') != 'pass':
            d['fail'] += 1
        d['rows'].append({
            'time': ts[11:16],
            'scenario': r.get('scenario_label', r.get('scenario_id', '')),
            'level': LEVEL_LABEL.get(r.get('level'), r.get('level', '')),
            'result': r.get('result', ''),
            'latency': r.get('latency_ms', ''),
            'note': r.get('note', '') or r.get('stt_text', ''),
        })
    out = sorted(days_map.values(), key=lambda x: x['date'], reverse=True)
    today = datetime.date.today().isoformat()
    for d in out:
        d['rows'].sort(key=lambda x: x['time'], reverse=True)
        d['is_today'] = (d['date'] == today)
    return {'days': out, 'fetched': datetime.datetime.now().strftime('%H:%M:%S')}


def start_action(label, argv):
    """조작을 하위 프로세스로 실행 (한 번에 하나). argv는 rig 폴더 기준."""
    with ACTION['lock']:
        if ACTION['running']:
            return False, f"이미 실행 중입니다: {ACTION['label']}"
        ACTION['running'] = True
        ACTION['label'] = label
        ACTION['output'] = ''

    def run():
        env = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONUNBUFFERED='1')
        try:
            proc = subprocess.Popen([sys.executable] + argv, cwd=BASE_DIR,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    encoding='utf-8', errors='replace', env=env)
            for line in proc.stdout:
                ACTION['output'] += line
            proc.wait()
            ACTION['output'] += f'\n[종료 코드 {proc.returncode}]'
        except Exception as e:
            ACTION['output'] += f'\n[실행 오류] {e}'
        finally:
            ACTION['running'] = False

    threading.Thread(target=run, daemon=True).start()
    return True, '시작했습니다'


def handle_action(req):
    kind = req.get('kind')
    if kind == 'mic':
        return start_action('마이크 테스트', ['fieldcheck.py', '--mic-test'])
    if kind == 'snap':
        cfg = load_cfg()
        return start_action('카메라 스냅샷',
                            ['vision.py', '--snapshot', '--device', str(camera_device(cfg))])
    if kind == 'once':
        argv = ['fieldcheck.py', '--once']
        if req.get('force'):
            argv.append('--force')
        return start_action('전체 점검', argv)
    if kind == 'synth':
        text = str(req.get('text', '')).strip()
        name = str(req.get('filename', '')).strip()
        if not text:
            return False, '합성할 문장을 입력해 주세요'
        if not SAFE_WAV.match(name):
            return False, '파일명은 영문·숫자·밑줄에 .wav 형식이어야 합니다 (예: combo_on.wav)'
        # 재현성 원칙 보호: 기존 파일은 덮어쓰기 전에 자동 백업
        full = os.path.join(PHRASE_DIR, name)
        if os.path.isfile(full):
            os.makedirs(PHRASE_BACKUP_DIR, exist_ok=True)
            stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            shutil.copy2(full, os.path.join(PHRASE_BACKUP_DIR, f'{stamp}_{name}'))
        return start_action(f'음성 생성({name})',
                            ['synthesize_phrases.py', text, os.path.join('phrases', name)])
    return False, '알 수 없는 조작입니다'


PAGE = """<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ThinQ ON 자동 점검 제어판</title>
<style>
:root { --olive:#3a5035; --olive-soft:#eff3ec; --bg:#f4f3ef; --card:#fff; --muted:#63635e; --line:#e2e0d8; --amber:#a8803a; }
* { box-sizing:border-box; margin:0; }
body { font-family:'Pretendard','Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif;
       background:var(--bg); color:#1e1e1b; padding:18px; font-size:14px;
       -webkit-font-smoothing:antialiased; }
h1 { font-size:22px; color:var(--olive); margin-bottom:3px; letter-spacing:-0.3px; }
.sub { color:var(--muted); font-size:13px; margin-bottom:12px; }
.tabs { display:flex; gap:6px; margin-bottom:14px; border-bottom:2px solid var(--line); }
.tabs button { background:none; color:var(--muted); border:none; border-bottom:3px solid transparent;
               border-radius:0; padding:9px 16px; font-size:15px; font-weight:700; margin:0; cursor:pointer; }
.tabs button.on { color:var(--olive); border-bottom-color:var(--olive); }
.grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:12px; margin-bottom:12px; }
.card { background:var(--card); border:1px solid var(--line); border-radius:10px; padding:14px; margin-bottom:12px; }
.card h2 { font-size:14px; color:var(--olive); margin:-4px -4px 10px -4px;
           background:var(--olive-soft); border-left:4px solid var(--olive);
           padding:7px 10px; border-radius:6px; font-weight:700; }
.row { display:flex; justify-content:space-between; font-size:14px; padding:4px 0; border-bottom:1px dashed var(--line); }
.row:last-child { border-bottom:none; }
.ok { color:var(--olive); font-weight:700; } .bad { color:#9c4a40; font-weight:700; }
button { background:var(--olive); color:#fff; border:none; border-radius:8px; padding:11px 15px; font-size:14px; font-weight:600; cursor:pointer; margin:3px 4px 3px 0; font-family:inherit; }
button:disabled { background:#b6b3a8; cursor:not-allowed; }
button.warn { background:var(--amber); }
button.mini { padding:5px 10px; font-size:12.5px; }
label { font-size:13px; color:var(--muted); }
input[type=text] { font-family:inherit; font-size:14px; padding:9px 10px; border:1px solid var(--line); border-radius:8px; }
select { font-family:inherit; font-size:14px; padding:9px 8px; border:1px solid var(--line); border-radius:8px; background:#fff; }
pre { background:#23241f; color:#e8e6da; border-radius:8px; padding:12px; font-size:12.5px; line-height:1.55; max-height:320px; overflow:auto; white-space:pre-wrap; }
table { width:100%; border-collapse:collapse; font-size:13.5px; }
td,th { padding:6px 7px; border-bottom:1px solid var(--line); text-align:left; }
th { position:sticky; top:0; background:var(--card); color:var(--muted); font-weight:600; }
audio { width:220px; height:30px; }
img.thumb { max-width:220px; border-radius:6px; display:block; }
.muted { color:var(--muted); font-size:13px; }
.banner { background:#fbf6ec; border:1px solid #e8d9b8; border-radius:8px; padding:10px 12px; font-size:13px; margin-bottom:12px; }
.tag { display:inline-block; background:var(--olive-soft); color:var(--olive); border-radius:6px; padding:2px 8px; font-size:12px; font-weight:700; margin-left:6px; }
#results, #recs { max-height:380px; overflow-y:auto; }
.day-head { display:flex; justify-content:space-between; align-items:center; }
</style></head><body>
<h1>ThinQ ON 자동 점검 제어판</h1>
<div class="sub">FieldCheck 점검 장비 — 이 창은 이 컴퓨터에서만 접속됩니다</div>

<div class="tabs">
  <button id="tabbtn-main" class="on" onclick="showTab('main')">현황</button>
  <button id="tabbtn-tts" onclick="showTab('tts')">점검 음성</button>
  <button id="tabbtn-report" onclick="showTab('report')">결과서</button>
</div>

<div id="tab-main">
  <div class="grid">
    <div class="card"><h2>장비 상태</h2><div id="devs">불러오는 중...</div></div>
    <div class="card"><h2>설정 요약</h2><div id="cfg">불러오는 중...</div></div>
    <div class="card"><h2>자동 실행 로그 (마지막)</h2><pre id="sched" style="max-height:120px">불러오는 중...</pre></div>
  </div>

  <div class="card">
    <h2>조작</h2>
    <button onclick="act({kind:'mic'})">마이크 테스트 (3초)</button>
    <button onclick="act({kind:'snap'})">카메라 스냅샷</button>
    <button class="warn" onclick="runOnce()">전체 점검 실행</button>
    <label><input type="checkbox" id="force"> 예약 회피 무시(--force)</label>
    <div class="muted" style="margin-top:6px">⚠ 전체 점검은 결과가 운영 시트로 전송됩니다 — ThinQ Real 현장에서만 실행하세요. 점검 중에는 개입(조명·커튼 조작) 금지.</div>
  </div>

  <div class="grid">
    <div class="card"><h2>최근 판정 결과 (이 장비)</h2><div id="results">불러오는 중...</div></div>
    <div class="card"><h2>기록 (녹음·스냅샷)</h2><div id="recs">불러오는 중...</div></div>
  </div>
</div>

<div id="tab-tts" style="display:none">
  <div class="banner">⚠ <b>재현성 원칙</b>: 점검 음성을 바꾸면 그날부터 "같은 입력"이 아니게 되어 이전 데이터와의 비교 기준이 달라집니다.
  꼭 필요할 때만 바꾸고, 바꾼 날짜를 기억해 두세요. 기존 파일은 <b>phrases/backups/</b>에 자동 백업됩니다.
  사람 목소리로 녹음한 파일(외출 모드 등)을 합성으로 덮어쓰면 인식률이 떨어질 수 있으니 주의하세요.</div>

  <div class="card">
    <h2>새 음성 만들기 (OS 음성합성)</h2>
    <div style="display:flex; gap:8px; flex-wrap:wrap; align-items:center">
      <input type="text" id="synthText" placeholder="합성할 문장 (예: 거실 다운라이트 켜고, 거실 커튼도 열어줘)" style="flex:1; min-width:260px">
      <select id="synthName"></select>
      <input type="text" id="synthNameCustom" placeholder="새 파일명.wav" style="display:none; width:170px">
      <button onclick="synth()">생성</button>
    </div>
    <div class="muted" style="margin-top:6px">생성 후 아래 목록에서 재생해 확인하고, ThinQ ON 인식은 현장에서 점검으로 확인하세요.</div>
  </div>

  <div class="card"><h2>음성 파일 목록</h2><div id="phrases">불러오는 중...</div></div>
</div>

<div id="tab-report" style="display:none">
  <div class="banner">아침 요약 메일(결과서)은 서버가 <b>운영 시트의 기록</b>으로 만들어 발송합니다.
  아래는 같은 기록을 날짜별로 정리한 것입니다 — <b>오늘 날짜 = 내일 아침 결과서에 실릴 내용</b>입니다.
  이 장비뿐 아니라 모든 점검 장비의 기록이 합쳐져 보입니다.</div>
  <div class="card">
    <div class="day-head"><h2 style="flex:1">최근 7일 점검 결과 (운영 시트)</h2>
      <button class="mini" onclick="loadReports()">새로고침</button></div>
    <div id="reports" class="muted">"새로고침"을 누르면 서버에서 불러옵니다 (처음엔 수 초 걸릴 수 있음)</div>
  </div>
</div>

<pre id="out" style="display:none"></pre>
<div class="muted">새로고침(F5)하면 상태·목록이 갱신됩니다 · 종료는 검은 서버 창을 닫으면 됩니다</div>

<script>
function esc(s){ return String(s??'').replace(/[&<>"]/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }
function showTab(t){
  for (const x of ['main','tts','report']){
    document.getElementById('tab-'+x).style.display = (x===t)?'':'none';
    document.getElementById('tabbtn-'+x).classList.toggle('on', x===t);
  }
  if (t==='tts' && !window._ttsLoaded){ loadPhrases(); window._ttsLoaded=true; }
}
async function status(){
  const r = await fetch('/api/status'); const d = await r.json();
  const a = d.audio;
  function devRow(t, x){
    if(!x) return `<div class="row"><span>${t}</span><span class="bad">확인 불가</span></div>`;
    return `<div class="row"><span>${t} (${esc(x.spec)})</span><span class="${x.ok?'ok':'bad'}">${x.ok?(x.name?esc(x.name):'정상'):'연결 안 됨'}</span></div>`;
  }
  document.getElementById('devs').innerHTML =
    devRow('마이크', a.input) + devRow('스피커', a.output) +
    `<div class="row"><span>카메라 번호</span><span>${d.camera} <span class="muted">(연결 확인은 스냅샷 버튼)</span></span></div>` +
    (a.note?`<div class="muted">${esc(a.note)}</div>`:'');
  document.getElementById('cfg').innerHTML = d.cfg_rows.map(x=>
    `<div class="row"><span>${esc(x[0])}</span><span>${esc(x[1])}</span></div>`).join('');
  document.getElementById('sched').textContent = d.sched;
  document.getElementById('results').innerHTML = d.results.length ?
    '<table><tr><th>시각</th><th>시나리오</th><th>단계</th><th>결과</th></tr>' + d.results.map(x=>
      `<tr><td>${esc(x.time.slice(5))}</td><td>${esc(x.scenario)}</td><td>${esc(x.level)}</td>`+
      `<td class="${x.result==='pass'?'ok':'bad'}">${x.result==='pass'?'통과':'실패'}</td></tr>`).join('')+'</table>'
    : '<div class="muted">기록 없음 (첫 점검 전)</div>';
}
async function recs(){
  const r = await fetch('/api/recordings'); const d = await r.json();
  document.getElementById('recs').innerHTML = d.length ? d.map(x=>{
    const media = x.kind==='audio' ? `<audio controls preload="none" src="/rec/${x.rel}"></audio>`
      : `<a href="/rec/${x.rel}" target="_blank"><img class="thumb" loading="lazy" src="/rec/${x.rel}"></a>`;
    return `<div style="padding:6px 0;border-bottom:1px dashed var(--line)"><div class="muted">${x.time} · ${esc(x.rel)} · ${x.size_kb}KB</div>${media}</div>`;
  }).join('') : '<div class="muted">기록 없음</div>';
}
async function loadPhrases(){
  const r = await fetch('/api/phrases'); const d = await r.json();
  document.getElementById('phrases').innerHTML = d.length ? d.map(x=>{
    const media = x.size_kb==null ? '<span class="bad">파일 없음 — 위에서 생성 필요</span>'
      : `<audio controls preload="none" src="/phrase/${x.name}"></audio>`;
    return `<div style="padding:7px 0;border-bottom:1px dashed var(--line)">
      <div><b>${esc(x.name)}</b><span class="tag">${x.roles.map(esc).join(' · ')}</span>
      <span class="muted"> ${x.size_kb!=null?x.size_kb+'KB · ':''}${esc(x.time)}</span></div>${media}</div>`;
  }).join('') : '<div class="muted">음성 파일이 없습니다</div>';
  const sel = document.getElementById('synthName');
  sel.innerHTML = d.filter(x=>x.size_kb!=null||true).map(x=>`<option value="${esc(x.name)}">${esc(x.name)}</option>`).join('')
    + '<option value="__custom__">직접 입력...</option>';
  sel.onchange = ()=>{ document.getElementById('synthNameCustom').style.display =
    sel.value==='__custom__' ? '' : 'none'; };
}
function synth(){
  const text = document.getElementById('synthText').value.trim();
  const sel = document.getElementById('synthName');
  const name = sel.value==='__custom__' ? document.getElementById('synthNameCustom').value.trim() : sel.value;
  if(!text){ alert('합성할 문장을 입력해 주세요'); return; }
  if(!name){ alert('파일명을 선택하거나 입력해 주세요'); return; }
  if(!confirm(`"${text}"\\n→ phrases/${name} 로 생성합니다.\\n기존 파일이 있으면 backups/에 백업 후 교체됩니다. 진행할까요?`)) return;
  act({kind:'synth', text, filename:name}, ()=>{ window._ttsLoaded=false; showTab('tts'); });
}
async function loadReports(){
  const el = document.getElementById('reports');
  el.innerHTML = '<span class="muted">서버에서 불러오는 중... (수 초 걸릴 수 있음)</span>';
  const r = await fetch('/api/reports'); const d = await r.json();
  if(d.error){ el.innerHTML = `<span class="bad">${esc(d.error)}</span>`; return; }
  if(!d.days.length){ el.innerHTML = '<span class="muted">최근 7일 기록이 없습니다</span>'; return; }
  el.innerHTML = d.days.map(day=>{
    const head = `<div style="margin:10px 0 4px"><b>${esc(day.date)}</b>`+
      (day.is_today?'<span class="tag">오늘 — 내일 아침 결과서 내용</span>':'')+
      ` <span class="${day.fail? 'bad':'ok'}">${day.total}건 중 실패 ${day.fail}건</span></div>`;
    const rows = day.rows.map(x=>
      `<tr><td>${esc(x.time)}</td><td>${esc(x.scenario)}</td><td>${esc(x.level)}</td>`+
      `<td class="${x.result==='pass'?'ok':'bad'}">${x.result==='pass'?'통과':'실패'}</td>`+
      `<td class="muted">${esc(String(x.note).slice(0,60))}</td></tr>`).join('');
    return head + `<div style="max-height:260px;overflow-y:auto"><table>`+
      `<tr><th>시각</th><th>시나리오</th><th>단계</th><th>결과</th><th>비고</th></tr>${rows}</table></div>`;
  }).join('') + `<div class="muted" style="margin-top:8px">불러온 시각: ${esc(d.fetched)}</div>`;
}
let polling = null;
async function poll(){
  const r = await fetch('/api/output'); const d = await r.json();
  const out = document.getElementById('out');
  out.style.display='block'; out.textContent = d.output || '(실행 중...)';
  out.scrollTop = out.scrollHeight;
  if(!d.running){
    clearInterval(polling); polling=null; status(); recs();
    if (window._afterAction){ const f=window._afterAction; window._afterAction=null; f(); }
  }
}
async function act(req, after){
  const r = await fetch('/api/action', {method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify(req)});
  const d = await r.json();
  if(!d.ok){ alert(d.msg); return; }
  window._afterAction = after || null;
  document.getElementById('out').textContent='';
  if(!polling) polling = setInterval(poll, 1000);
}
function runOnce(){
  const force = document.getElementById('force').checked;
  if(!confirm('전체 점검을 실행합니다. 결과가 운영 시트로 전송됩니다.\\nThinQ Real 현장이 맞습니까?')) return;
  act({kind:'once', force});
}
status(); recs();
</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # 콘솔을 조용히 유지

    def _send(self, code, body, ctype='application/json; charset=utf-8'):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_file(self, base_dir, rel, kinds=('.wav', '.jpg', '.jpeg', '.png')):
        full = os.path.normpath(os.path.join(base_dir, rel))
        if not full.startswith(os.path.normpath(base_dir)) or not os.path.isfile(full) \
                or not full.lower().endswith(kinds):
            self._send(404, {'error': 'not found'})
            return
        ctype = 'audio/wav' if full.lower().endswith('.wav') else 'image/jpeg'
        with open(full, 'rb') as f:
            self._send(200, f.read(), ctype)

    def do_GET(self):
        if self.path == '/':
            self._send(200, PAGE.encode('utf-8'), 'text/html; charset=utf-8')
        elif self.path == '/api/status':
            cfg = load_cfg()
            if cfg is None:
                self._send(200, {'audio': {'input': None, 'output': None,
                                           'note': 'config.json이 없거나 읽을 수 없습니다'},
                                 'camera': '-', 'cfg_rows': [], 'sched': '', 'results': []})
                return
            cal = cfg.get('dba_calibration_offset', 0)
            self._send(200, {
                'audio': audio_status(cfg),
                'camera': camera_device(cfg),
                'cfg_rows': [
                    ['시나리오', f"{len(cfg.get('scenarios', []))}개"],
                    ['점검 시간대', str(cfg.get('active_hours', '-'))],
                    ['dBA 보정', f'{cal}' + ('' if cal else ' (미보정)')],
                    ['예약 회피', '켜짐' if (cfg.get('booking_avoidance') or {}).get('enabled', True) else '꺼짐'],
                    ['내용 점검(STT)', '켜짐' if (cfg.get('stt') or {}).get('enabled') else '꺼짐'],
                ],
                'sched': sched_tail(),
                'results': recent_results(),
            })
        elif self.path == '/api/recordings':
            self._send(200, list_recordings())
        elif self.path == '/api/phrases':
            self._send(200, list_phrases())
        elif self.path == '/api/reports':
            self._send(200, fetch_reports())
        elif self.path == '/api/output':
            self._send(200, {'running': ACTION['running'], 'output': ACTION['output']})
        elif self.path.startswith('/rec/'):
            self._send_file(REC_DIR, self.path[len('/rec/'):])
        elif self.path.startswith('/phrase/'):
            name = os.path.basename(self.path[len('/phrase/'):])
            self._send_file(PHRASE_DIR, name, kinds=('.wav',))
        else:
            self._send(404, {'error': 'not found'})

    def do_POST(self):
        if self.path != '/api/action':
            self._send(404, {'error': 'not found'})
            return
        try:
            length = int(self.headers.get('Content-Length', 0))
            req = json.loads(self.rfile.read(length) or b'{}')
        except (ValueError, json.JSONDecodeError):
            req = {}
        ok, msg = handle_action(req)
        self._send(200, {'ok': ok, 'msg': msg})


def main():
    addr = ('127.0.0.1', PORT)
    url = f'http://127.0.0.1:{PORT}'
    try:
        server = ThreadingHTTPServer(addr, Handler)
    except OSError:
        print(f'제어판이 이미 실행 중입니다 — 브라우저를 엽니다: {url}')
        webbrowser.open(url)
        return
    print('ThinQ ON 자동 점검 제어판을 시작합니다.')
    print(f'  주소: {url}  (이 컴퓨터에서만 접속 가능)')
    print('  종료: 이 창을 닫거나 Ctrl+C')
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n제어판을 종료합니다.')


if __name__ == '__main__':
    main()
