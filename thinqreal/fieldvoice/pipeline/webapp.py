#!/usr/bin/env python3
"""FieldVoice 웹 UI — 업로드 → 파이프라인 실행 → 진행 상황 → 결과 열람.

run.sh로 기동. 로컬 전용(127.0.0.1) — 녹음·전사가 다뤄지므로 외부 바인딩 금지.
"""
import datetime
import json
import threading
import uuid
import webbrowser
from pathlib import Path

import requests
from flask import Flask, jsonify, render_template_string, request, abort

import pipeline

BASE = Path(__file__).resolve().parent
UPLOADS = BASE / "uploads"
UPLOADS.mkdir(exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024 * 1024  # 1GB

RUNS = {}  # run_id -> {stages:{key:{status,detail}}, error, session, done}
ALLOWED_EXTS = pipeline.stt.AUDIO_EXTS | {".txt", ".md"}


def _new_run():
    rid = uuid.uuid4().hex[:8]
    RUNS[rid] = {
        "stages": {k: {"status": "wait", "detail": ""} for k, _ in pipeline.STAGES},
        "error": None, "session": None, "done": False,
    }
    return rid


def _worker(rid, path, name):
    run = RUNS[rid]

    def progress(stage, status, detail=""):
        run["stages"][stage] = {"status": status, "detail": detail}

    try:
        outdir = pipeline.run_pipeline(path, name=name, progress=progress)
        run["session"] = outdir.name
    except Exception as e:  # 단계 어디서든 실패를 UI에 그대로 보여준다
        run["error"] = str(e)
        for st in run["stages"].values():
            if st["status"] == "running":
                st["status"] = "error"
    finally:
        run["done"] = True


@app.post("/run")
def start_run():
    if request.form.get("sample"):
        path = BASE / "sample" / "sample_transcript.txt"
        name = "샘플"
    else:
        f = request.files.get("file")
        if not f or not f.filename:
            return jsonify({"error": "파일이 없습니다"}), 400
        suffix = Path(f.filename).suffix.lower()
        if suffix not in ALLOWED_EXTS:
            return jsonify({"error": f"지원하지 않는 형식: {suffix}"}), 400
        path = UPLOADS / f"{uuid.uuid4().hex[:8]}_{Path(f.filename).name}"
        f.save(path)
        name = request.form.get("name") or Path(f.filename).stem
    rid = _new_run()
    threading.Thread(target=_worker, args=(rid, path, name), daemon=True).start()
    return jsonify({"id": rid})


@app.get("/status/<rid>")
def status(rid):
    run = RUNS.get(rid)
    if not run:
        abort(404)
    return jsonify({
        "stages": [
            {"key": k, "label": lbl, **run["stages"][k]} for k, lbl in pipeline.STAGES
        ],
        "error": run["error"], "session": run["session"], "done": run["done"],
    })


@app.get("/sessions")
def sessions():
    out = []
    if pipeline.OUTPUT_ROOT.exists():
        for mf in sorted(pipeline.OUTPUT_ROOT.glob("*/session.json"), reverse=True):
            try:
                out.append(json.loads(mf.read_text(encoding="utf-8")))
            except (json.JSONDecodeError, OSError):
                continue
    return jsonify(out)


@app.get("/file/<sid>/<fname>")
def get_file(sid, fname):
    # 경로 탈출 방지: 세션 매니페스트에 등록된 파일명만 허용
    mf = pipeline.OUTPUT_ROOT / sid / "session.json"
    if not mf.exists():
        abort(404)
    manifest = json.loads(mf.read_text(encoding="utf-8"))
    if fname not in manifest.get("files", []):
        abort(404)
    return (pipeline.OUTPUT_ROOT / sid / fname).read_text(encoding="utf-8"), 200, {
        "Content-Type": "text/plain; charset=utf-8"
    }


def _extract_one_liner(md):
    """report.md의 '## 한 줄 결론' 섹션 첫 문단을 목록 표시용으로 추출."""
    lines = md.splitlines()
    for i, line in enumerate(lines):
        if line.strip().startswith("## 한 줄 결론"):
            for nxt in lines[i + 1:]:
                t = nxt.strip()
                if t.startswith("#"):
                    break
                if t:
                    return t[:300]
    return ""


@app.post("/upload/<sid>")
def upload_report(sid):
    """1페이지 요약(report.md)을 관리자 페이지(voc_reports)로 업로드.
    도슨트가 가명화를 확인한 뒤 버튼으로만 호출되는 수동 게이트 (DESIGN.md §8)."""
    up = pipeline.load_config().get("upload") or {}
    key = str(up.get("api_key") or "")
    if not up.get("endpoint_url") or not key or "여기에" in key:
        return jsonify({"error": "업로드 미설정 — config.json에 upload.api_key(FV_API_KEY 값)를 넣으세요 (README §6)"}), 400

    if not (pipeline.OUTPUT_ROOT / sid / "session.json").exists():
        abort(404)
    report_path = pipeline.OUTPUT_ROOT / sid / "report.md"
    if not report_path.exists():
        return jsonify({"error": "report.md가 없습니다 — 분석을 먼저 완료하세요"}), 404
    md = report_path.read_text(encoding="utf-8")

    form = request.get_json(silent=True) or {}
    payload = {
        "type": "voc_report",
        "apiKey": key,
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "session_id": sid,
        "visit_date": form.get("visit_date") or "",
        "purpose": form.get("purpose") or "",
        "author": form.get("author") or "",
        "consent": form.get("consent") or "구두",
        "one_liner": _extract_one_liner(md),
        "report_md": md,
    }
    try:
        r = requests.post(up["endpoint_url"], json=payload, timeout=60)
        data = r.json()
    except requests.RequestException as e:
        return jsonify({"error": f"전송 실패: {e}"}), 502
    except ValueError:
        return jsonify({"error": "서버 응답 형식 오류 — 배포 URL을 확인하세요"}), 502
    if not data.get("success"):
        return jsonify({"error": f"서버 거부: {data.get('error', '원인 미상')}"}), 502
    return jsonify({"success": True, "id": data.get("id")})


@app.get("/")
def index():
    return render_template_string(PAGE)


PAGE = r"""<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>FieldVoice</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
  :root { --olive:#3a5035; --olive-soft:#eef1ec; --ink:#1d1d1f; --sub:#6e6e73;
          --line:#e5e5ea; --bad:#9c4a40; --warn:#a8803a; }
  * { box-sizing:border-box; margin:0; }
  body { font-family:Inter,-apple-system,"Apple SD Gothic Neo",sans-serif; color:var(--ink);
         background:#fafafa; padding:32px 16px; }
  .wrap { max-width:880px; margin:0 auto; }
  h1 { font-size:22px; letter-spacing:-.02em; }
  h1 small { color:var(--sub); font-weight:400; font-size:13px; margin-left:8px; }
  .card { background:#fff; border:1px solid var(--line); border-radius:14px; padding:20px; margin-top:16px; }
  .row { display:flex; gap:10px; flex-wrap:wrap; align-items:center; }
  input[type=file] { flex:1; min-width:220px; font-size:13px; }
  button { background:var(--olive); color:#fff; border:0; border-radius:9px; padding:10px 16px;
           font-size:14px; font-weight:600; cursor:pointer; min-height:44px; }
  button.ghost { background:var(--olive-soft); color:var(--olive); }
  button:disabled { opacity:.45; cursor:default; }
  .hint { font-size:12px; color:var(--sub); margin-top:10px; line-height:1.6; }
  .stage { display:flex; align-items:center; gap:10px; padding:8px 0; border-bottom:1px solid var(--olive-soft); font-size:14px; }
  .stage:last-child { border-bottom:0; }
  .dot { width:22px; height:22px; border-radius:50%; display:flex; align-items:center; justify-content:center;
         font-size:12px; background:var(--line); color:var(--sub); flex:none; }
  .dot.running { background:var(--warn); color:#fff; animation:pulse 1.2s infinite; }
  .dot.done { background:var(--olive); color:#fff; }
  .dot.skipped { background:var(--olive-soft); color:var(--olive); }
  .dot.error { background:var(--bad); color:#fff; }
  @keyframes pulse { 50% { opacity:.55; } }
  .detail { color:var(--sub); font-size:12px; }
  .error-box { background:#fdf1ef; border:1px solid var(--bad); color:var(--bad);
               border-radius:9px; padding:12px; font-size:13px; margin-top:12px; white-space:pre-wrap; }
  .tabs { display:flex; gap:6px; flex-wrap:wrap; margin-bottom:14px; }
  .tabs button { min-height:34px; padding:6px 12px; font-size:13px; }
  .tabs button.off { background:var(--olive-soft); color:var(--olive); }
  #viewer { font-size:14px; line-height:1.75; overflow-x:auto; }
  #viewer h1,#viewer h2,#viewer h3 { margin:18px 0 8px; letter-spacing:-.01em; }
  #viewer h2 { font-size:17px; color:var(--olive); }
  #viewer blockquote { border-left:3px solid var(--olive); padding-left:12px; color:var(--sub); margin:8px 0; }
  #viewer pre { background:var(--olive-soft); padding:12px; border-radius:9px; overflow-x:auto; font-size:12.5px; }
  #viewer table { border-collapse:collapse; } #viewer td,#viewer th { border:1px solid var(--line); padding:6px 10px; font-size:13px; }
  .sess { padding:10px 0; border-bottom:1px solid var(--olive-soft); font-size:13.5px; display:flex;
          justify-content:space-between; gap:8px; cursor:pointer; }
  .sess:hover { color:var(--olive); }
  .sess .meta { color:var(--sub); font-size:12px; }
</style></head><body><div class="wrap">
<h1>🎙 FieldVoice <small>인터뷰 맥락 분석·인사이트 파이프라인</small></h1>

<div class="card">
  <div class="row">
    <input type="file" id="file" accept=".wav,.mp3,.m4a,.mp4,.aac,.flac,.ogg,.webm,.txt,.md">
    <button id="go">분석 시작</button>
    <button id="demo" class="ghost">샘플 전사로 시험</button>
  </div>
  <div class="hint">오디오(wav·mp3·m4a…) 또는 전사 텍스트(.txt)를 올리면
  전사 → 화자 라벨링 → 요약 → 맥락 분석 → 인사이트까지 자동 실행됩니다.<br>
  ⚠ 모든 처리는 이 컴퓨터 안에서만 이뤄지며(전사 로컬·분석은 Claude API), 결과물은
  <code>pipeline/output/</code>에 저장됩니다 — 녹음·전사·리포트는 저장소에 커밋 금지.</div>
</div>

<div class="card" id="progress" style="display:none">
  <div id="stages"></div>
  <div class="error-box" id="err" style="display:none"></div>
</div>

<div class="card" id="result" style="display:none">
  <div class="tabs" id="tabs"></div>
  <div id="viewer"></div>
  <div style="margin-top:16px;padding-top:14px;border-top:1px solid var(--line)">
    <b style="font-size:13.5px">관리자 페이지로 업로드</b>
    <span class="detail">— 요약 리포트(report.md)만 전송. 업로드 전 가명화(이름·회사명) 확인 필수</span>
    <div class="row" style="margin-top:10px">
      <input type="date" id="upDate" style="min-width:130px;flex:none">
      <select id="upPurpose">
        <option>B2B</option><option>R&D</option><option>내부 행사</option>
        <option>Press Tour</option><option>기타</option>
      </select>
      <input type="text" id="upAuthor" placeholder="작성자" style="flex:none;width:100px">
      <select id="upConsent"><option value="구두">동의: 구두</option><option value="서면">동의: 서면</option></select>
      <button id="upBtn" class="ghost">업로드</button>
    </div>
    <div class="hint" id="upMsg"></div>
  </div>
</div>

<div class="card">
  <b style="font-size:14px">지난 세션</b>
  <div id="sessions" class="hint">없음</div>
</div>

<script>
const FILES = [["report.md","요약 리포트"],["report_full.md","전체 리포트"],["05_insights.md","인사이트"],
               ["04_context.md","맥락 분석"],["03_summary.md","요약"],["02_labeled.md","라벨 전사"],
               ["01_transcript.md","원본 전사"]];
const $ = id => document.getElementById(id);
let timer = null;

async function start(form) {
  $("go").disabled = $("demo").disabled = true;
  $("progress").style.display = "block"; $("result").style.display = "none";
  $("err").style.display = "none";
  const r = await fetch("/run", {method:"POST", body:form});
  const j = await r.json();
  if (j.error) { showErr(j.error); return; }
  timer = setInterval(() => poll(j.id), 1200);
}

async function poll(rid) {
  const s = await (await fetch("/status/"+rid)).json();
  $("stages").innerHTML = s.stages.map(st => {
    const icon = {wait:"○", running:"…", done:"✓", skipped:"―", error:"✗"}[st.status] || "○";
    return `<div class="stage"><span class="dot ${st.status}">${icon}</span>
      <span>${st.label}</span><span class="detail">${st.detail||""}</span></div>`;
  }).join("");
  if (s.error) { clearInterval(timer); showErr(s.error); }
  if (s.done && !s.error) { clearInterval(timer); $("go").disabled = $("demo").disabled = false;
    loadSessions(); openSession(s.session); }
}

function showErr(msg) { $("err").textContent = msg; $("err").style.display = "block";
  $("go").disabled = $("demo").disabled = false; }

let curSid = null;
async function openSession(sid) {
  curSid = sid;
  $("upMsg").textContent = "";
  $("result").style.display = "block";
  $("tabs").innerHTML = FILES.map(([f,l],i) =>
    `<button class="${i?'off':''}" onclick="openFile('${sid}','${f}',this)">${l}</button>`).join("");
  openFile(sid, "report.md", null);
}

async function openFile(sid, fname, btn) {
  if (btn) { document.querySelectorAll("#tabs button").forEach(b=>b.classList.add("off"));
             btn.classList.remove("off"); }
  const r = await fetch(`/file/${sid}/${fname}`);
  const text = r.ok ? await r.text() : "(파일 없음)";
  $("viewer").innerHTML = (window.marked) ? marked.parse(text)
    : "<pre>"+text.replace(/</g,"&lt;")+"</pre>";
  $("result").scrollIntoView({behavior:"smooth"});
}

async function loadSessions() {
  const list = await (await fetch("/sessions")).json();
  $("sessions").innerHTML = list.length ? list.map(m =>
    `<div class="sess" onclick="openSession('${m.id}')"><span>${m.id}</span>
     <span class="meta">${m.source} · ${m.created.replace("T"," ")}</span></div>`).join("") : "없음";
}

$("go").onclick = () => {
  const f = $("file").files[0];
  if (!f) { alert("파일을 선택하세요"); return; }
  const form = new FormData(); form.append("file", f); start(form);
};
$("demo").onclick = () => { const form = new FormData(); form.append("sample","1"); start(form); };
$("upBtn").onclick = async () => {
  if (!curSid) { alert("먼저 세션을 여세요"); return; }
  if (!$("upDate").value) { $("upMsg").textContent = "방문일을 선택하세요."; return; }
  if (!confirm("요약 리포트에 실명·회사명이 남아 있지 않은지 확인하셨나요?\n확인 후 관리자 페이지로 업로드합니다.")) return;
  $("upBtn").disabled = true; $("upMsg").textContent = "업로드 중…";
  try {
    const r = await fetch("/upload/" + curSid, { method:"POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ visit_date: $("upDate").value, purpose: $("upPurpose").value,
                             author: $("upAuthor").value, consent: $("upConsent").value }) });
    const j = await r.json();
    $("upMsg").textContent = j.success ? "✓ 업로드 완료 — 관리자 페이지 🎙 현장 인사이트 탭에서 확인하세요."
                                       : "실패: " + (j.error || "원인 미상");
  } catch (e) { $("upMsg").textContent = "실패: " + e; }
  $("upBtn").disabled = false;
};
loadSessions();
</script></div></body></html>"""


if __name__ == "__main__":
    cfg = pipeline.load_config()
    port = int(cfg.get("port", 8765))
    threading.Timer(1.0, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()
    print(f"FieldVoice 웹 UI: http://127.0.0.1:{port}  (종료: Ctrl+C)")
    app.run(host="127.0.0.1", port=port, debug=False)
