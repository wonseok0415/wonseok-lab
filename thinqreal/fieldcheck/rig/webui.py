#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
#  FieldCheck 조작판 — 로컬 웹 UI (순수 추가 기능)
#
#  코드·명령줄을 건드리지 않고 브라우저에서 점검 장비를 조작·확인한다:
#    · 상태: 마이크/스피커/카메라 설정과 실제 연결(이름 해석) 확인
#    · 조작: 마이크 테스트 / 카메라 스냅샷 / 전체 점검 실행 (버튼)
#    · 기록: 녹음(wav)·스냅샷(jpg)을 목록에서 바로 재생/보기
#    · 최근 판정 결과와 자동 실행 로그 요약
#
#  실행:  python webui.py     (브라우저가 자동으로 열림)
#  종료:  이 창을 닫거나 Ctrl+C
#
#  보안: 127.0.0.1 전용 — 같은 컴퓨터의 브라우저에서만 접속 가능하다.
#  기존 자동 점검(fieldcheck.py)에는 영향이 없다. 조작은 명령줄과 동일한
#  하위 프로세스 실행이라, UI로 하든 명령으로 하든 결과가 같다.
# ============================================================
import json
import os
import subprocess
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')
LOG_PATH = os.path.join(BASE_DIR, 'results.jsonl')
REC_DIR = os.path.join(BASE_DIR, 'recordings')
SCHED_LOG = os.path.join(BASE_DIR, 'logs', 'schedule.log')
PORT = 8477

LEVEL_LABEL = {'L1': '응답 점검', 'L2': '내용 점검', 'L3': '동작 점검'}

# 실행 중인 조작 (한 번에 하나 — 마이크·스피커·카메라는 공유 불가)
ACTION = {'running': False, 'kind': '', 'output': '', 'lock': threading.Lock()}

ACTIONS = {
    'mic': {'label': '마이크 테스트', 'cmd': ['fieldcheck.py', '--mic-test']},
    'snap': {'label': '카메라 스냅샷', 'cmd': None},  # 카메라 번호는 config에서 읽음
    'once': {'label': '전체 점검', 'cmd': ['fieldcheck.py', '--once']},
}


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


def start_action(kind, force=False):
    with ACTION['lock']:
        if ACTION['running']:
            return False, f"이미 실행 중입니다: {ACTIONS.get(ACTION['kind'], {}).get('label', ACTION['kind'])}"
        ACTION['running'] = True
        ACTION['kind'] = kind
        ACTION['output'] = ''

    if kind == 'snap':
        cfg = load_cfg()
        argv = ['vision.py', '--snapshot', '--device', str(camera_device(cfg))]
    else:
        argv = list(ACTIONS[kind]['cmd'])
        if kind == 'once' and force:
            argv.append('--force')

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


PAGE = """<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FieldCheck 조작판</title>
<style>
:root { --olive:#3a5035; --bg:#f4f3ef; --card:#fff; --muted:#6b6b66; --line:#e2e0d8; }
* { box-sizing:border-box; margin:0; }
body { font-family:'Malgun Gothic','Apple SD Gothic Neo',sans-serif; background:var(--bg); color:#22221f; padding:18px; }
h1 { font-size:20px; color:var(--olive); margin-bottom:2px; }
.sub { color:var(--muted); font-size:12px; margin-bottom:14px; }
.grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:12px; margin-bottom:12px; }
.card { background:var(--card); border:1px solid var(--line); border-radius:10px; padding:14px; }
.card h2 { font-size:13px; color:var(--olive); margin-bottom:8px; }
.row { display:flex; justify-content:space-between; font-size:13px; padding:3px 0; border-bottom:1px dashed var(--line); }
.row:last-child { border-bottom:none; }
.ok { color:var(--olive); font-weight:bold; } .bad { color:#9c4a40; font-weight:bold; }
button { background:var(--olive); color:#fff; border:none; border-radius:8px; padding:10px 14px; font-size:13px; cursor:pointer; margin:3px 4px 3px 0; }
button:disabled { background:#b6b3a8; cursor:not-allowed; }
button.warn { background:#a8803a; }
label { font-size:12px; color:var(--muted); }
pre { background:#23241f; color:#e8e6da; border-radius:8px; padding:12px; font-size:12px; line-height:1.5; max-height:320px; overflow:auto; white-space:pre-wrap; }
table { width:100%; border-collapse:collapse; font-size:12.5px; }
td,th { padding:5px 6px; border-bottom:1px solid var(--line); text-align:left; }
audio { width:220px; height:30px; }
img.thumb { max-width:220px; border-radius:6px; display:block; }
.muted { color:var(--muted); font-size:12px; }
</style></head><body>
<h1>FieldCheck 조작판</h1>
<div class="sub">ThinQ ON 자동 점검 장비 — 이 창은 이 컴퓨터에서만 접속됩니다</div>

<div class="grid">
  <div class="card"><h2>장비 상태</h2><div id="devs">불러오는 중...</div></div>
  <div class="card"><h2>설정 요약</h2><div id="cfg">불러오는 중...</div></div>
  <div class="card"><h2>자동 실행 로그 (마지막)</h2><pre id="sched" style="max-height:120px">불러오는 중...</pre></div>
</div>

<div class="card" style="margin-bottom:12px">
  <h2>조작</h2>
  <button onclick="act('mic')">마이크 테스트 (3초)</button>
  <button onclick="act('snap')">카메라 스냅샷</button>
  <button class="warn" onclick="runOnce()">전체 점검 실행</button>
  <label><input type="checkbox" id="force"> 예약 회피 무시(--force)</label>
  <div class="muted" style="margin-top:6px">⚠ 전체 점검은 결과가 운영 시트로 전송됩니다 — ThinQ Real 현장에서만 실행하세요. 점검 중에는 개입(조명·커튼 조작) 금지.</div>
  <pre id="out" style="margin-top:10px; display:none"></pre>
</div>

<div class="grid">
  <div class="card"><h2>최근 판정 결과</h2><div id="results">불러오는 중...</div></div>
  <div class="card"><h2>기록 (녹음·스냅샷)</h2><div id="recs">불러오는 중...</div></div>
</div>
<div class="muted">새로고침(F5)하면 상태·목록이 갱신됩니다 · 종료는 검은 서버 창을 닫으면 됩니다</div>

<script>
function esc(s){ return String(s??'').replace(/[&<>"]/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }
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
let polling = null;
async function poll(){
  const r = await fetch('/api/output'); const d = await r.json();
  const out = document.getElementById('out');
  out.style.display='block'; out.textContent = d.output || '(실행 중...)';
  out.scrollTop = out.scrollHeight;
  if(!d.running){ clearInterval(polling); polling=null; status(); recs(); }
}
async function act(kind, force){
  const r = await fetch('/api/action', {method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({kind, force:!!force})});
  const d = await r.json();
  if(!d.ok){ alert(d.msg); return; }
  document.getElementById('out').textContent='';
  if(!polling) polling = setInterval(poll, 1000);
}
function runOnce(){
  const force = document.getElementById('force').checked;
  if(!confirm('전체 점검을 실행합니다. 결과가 운영 시트로 전송됩니다.\\nThinQ Real 현장이 맞습니까?')) return;
  act('once', force);
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
        elif self.path == '/api/output':
            self._send(200, {'running': ACTION['running'], 'output': ACTION['output']})
        elif self.path.startswith('/rec/'):
            rel = self.path[len('/rec/'):]
            full = os.path.normpath(os.path.join(REC_DIR, rel))
            if not full.startswith(os.path.normpath(REC_DIR)) or not os.path.isfile(full):
                self._send(404, {'error': 'not found'})
                return
            ctype = 'audio/wav' if full.lower().endswith('.wav') else 'image/jpeg'
            with open(full, 'rb') as f:
                self._send(200, f.read(), ctype)
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
        kind = req.get('kind')
        if kind not in ACTIONS:
            self._send(400, {'ok': False, 'msg': '알 수 없는 조작입니다'})
            return
        ok, msg = start_action(kind, bool(req.get('force')))
        self._send(200, {'ok': ok, 'msg': msg})


def main():
    addr = ('127.0.0.1', PORT)
    url = f'http://127.0.0.1:{PORT}'
    try:
        server = ThreadingHTTPServer(addr, Handler)
    except OSError:
        print(f'조작판이 이미 실행 중입니다 — 브라우저를 엽니다: {url}')
        webbrowser.open(url)
        return
    print('FieldCheck 조작판을 시작합니다.')
    print(f'  주소: {url}  (이 컴퓨터에서만 접속 가능)')
    print('  종료: 이 창을 닫거나 Ctrl+C')
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n조작판을 종료합니다.')


if __name__ == '__main__':
    main()
