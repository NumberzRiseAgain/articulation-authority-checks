# Numberz.ai Inc.  Raghu Venkat (PI), Dr. Tricha Anjali.  Company-funded, September 2026.
# Feasibility study for DON26BZ05-NV071 (Navy / NAVAIR, SBIR Phase I). No Government funding.
# Released under the MIT License; see LICENSE at the repository root.
"""SPOKELINE — build the self-contained viewer page.

Three panes and one loop: the manual is the authority, the scenario is derived from it,
the checks run on every keystroke. Editing the manual regenerates the scenario. Injecting
a generator fault leaves the manual alone and makes the scenario diverge from it.
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aas as A, geometry as G, scenario as S

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def payload():
    a = A.extract(os.path.join(HERE, "corpus", "s1000d"))
    metrics = json.load(open(os.path.join(HERE, "runs", "latest", "metrics.json")))
    return {
        "manual": {"parts": a["parts"], "joints": a["joints"], "steps": a["steps"],
                   "constraints": a["constraints"], "markings": a["markings"]},
        "binding": G.TRUE_BINDING,
        "non_actionable": sorted(G.NON_ACTIONABLE),
        "segments": {k: {"c": v["c"], "h": v["h"], "pivot": v["pivot"]}
                     for k, v in G.SEGMENTS.items()},
        "metrics": metrics,
    }


HEAD = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SPOKELINE Authority Loop</title>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Serif:wght@400;500&display=swap">
<style>
:root{
  --ground:#EEF1F4;--surface:#FFFFFF;--surface-2:#F6F8FA;--edit:#FFFDF5;
  --ink:#101419;--ink-2:#4A555F;--ink-3:#77838D;
  --rule:#C6CCD2;--rule-2:#DDE2E7;
  --accent:#0B6E99;--accent-soft:#DCEDF5;
  --pass:#2F7A4D;--pass-soft:#DFEFE5;
  --hold:#B4342A;--hold-soft:#F7E0DE;
  --advisory:#9A6B10;--advisory-soft:#F6EBD4;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --ground:#0C1015;--surface:#151A21;--surface-2:#1B222B;--edit:#1E1B14;
  --ink:#E6EBF0;--ink-2:#A3AFBA;--ink-3:#76838F;
  --rule:#2B343E;--rule-2:#222A33;
  --accent:#4FB3E0;--accent-soft:#12303F;
  --pass:#5FC189;--pass-soft:#13301F;
  --hold:#F0776B;--hold-soft:#3A1A17;
  --advisory:#E0B057;--advisory-soft:#332711;
}}
:root[data-theme="dark"]{
  --ground:#0C1015;--surface:#151A21;--surface-2:#1B222B;--edit:#1E1B14;
  --ink:#E6EBF0;--ink-2:#A3AFBA;--ink-3:#76838F;
  --rule:#2B343E;--rule-2:#222A33;
  --accent:#4FB3E0;--accent-soft:#12303F;
  --pass:#5FC189;--pass-soft:#13301F;
  --hold:#F0776B;--hold-soft:#3A1A17;
  --advisory:#E0B057;--advisory-soft:#332711;
}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);font-size:13.5px;line-height:1.5;
  font-family:"IBM Plex Sans",system-ui,-apple-system,Segoe UI,sans-serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:1400px;margin:0 auto;padding:20px 18px 40px}
.mono{font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace;font-variant-numeric:tabular-nums}
.eyebrow{font-family:"IBM Plex Mono",monospace;font-size:10px;letter-spacing:.13em;
  text-transform:uppercase;color:var(--ink-3)}
.muted{color:var(--ink-3);font-size:11.5px}
header.top{border-bottom:2px solid var(--ink);padding-bottom:12px;
  display:flex;flex-wrap:wrap;gap:16px;align-items:flex-end;justify-content:space-between}
h1{font-size:24px;margin:3px 0 3px;font-weight:600;letter-spacing:-.015em}
.sub{color:var(--ink-2);max-width:74ch;margin:0}
.kpis{display:flex;gap:22px;flex-wrap:wrap}
.kpi .n{font-family:"IBM Plex Mono",monospace;font-size:21px;font-weight:600;line-height:1.1}
.kpi .l{font-size:10.5px;color:var(--ink-3)}
.flow{display:flex;align-items:center;gap:9px;margin:14px 0 4px;flex-wrap:wrap;
  font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--ink-2)}
.flow b{background:var(--accent-soft);color:var(--accent);padding:3px 8px;border-radius:2px;font-weight:600}
.flow span{color:var(--ink-3)}
.cols{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.15fr) minmax(0,.95fr);
  gap:16px;margin-top:12px;align-items:start}
@media(max-width:1150px){.cols{grid-template-columns:1fr 1fr}}
@media(max-width:800px){.cols{grid-template-columns:1fr}}
.panel{background:var(--surface);border:1px solid var(--rule);border-radius:3px;overflow:hidden}
.panel>.head{display:flex;align-items:center;justify-content:space-between;gap:10px;
  padding:8px 12px;border-bottom:1px solid var(--rule-2);background:var(--surface-2)}
.scrollpane{max-height:560px;overflow-y:auto}
.fld{font:inherit;font-size:12px;background:var(--edit);color:var(--ink);
  border:1px solid var(--rule);border-radius:2px;padding:2px 5px}
.fld:focus{outline:2px solid var(--accent);outline-offset:-1px;border-color:var(--accent)}
textarea.fld{width:100%;font-family:"IBM Plex Serif",Georgia,serif;font-size:13.5px;
  line-height:1.45;resize:vertical;margin:5px 0 6px}
.fld.num{width:62px;text-align:right}
.fld.ax{width:auto}
.dmhead{padding:8px 12px;border-bottom:1px solid var(--rule-2);font-size:10.5px;color:var(--ink-3)}
.jgroup{border-bottom:1px solid var(--rule-2);background:var(--surface-2)}
.jgroup summary{padding:7px 12px;cursor:pointer;font-size:11.5px;color:var(--ink-2)}
.jrows{padding:0 12px 9px}
.jrow{display:flex;align-items:center;gap:6px;flex-wrap:wrap;padding:3px 0;font-size:11.5px}
.jrow .pid{min-width:66px;color:var(--ink-2)}
.mstep{padding:10px 12px;border-bottom:1px solid var(--rule-2);cursor:pointer}
.mstep:hover{background:var(--surface-2)}
.mstep.sel{background:var(--accent-soft);box-shadow:inset 3px 0 0 var(--accent)}
.mhead{display:flex;justify-content:space-between;gap:8px;font-size:10.5px;color:var(--ink-3)}
.attrs{display:flex;align-items:center;gap:5px;flex-wrap:wrap;font-size:11.5px}
.lab{color:var(--ink-3);font-size:10px;letter-spacing:.06em;text-transform:uppercase}
.notice{border-left:3px solid;padding:6px 9px;margin-top:6px;font-size:12px;position:relative}
.notice.warning{border-color:var(--hold);background:var(--hold-soft)}
.notice.caution{border-color:var(--advisory);background:var(--advisory-soft)}
.notice.tool,.notice.torque{border-color:var(--accent);background:var(--accent-soft)}
.notice b{font-family:"IBM Plex Mono",monospace;font-size:9.5px;letter-spacing:.1em;
  text-transform:uppercase;display:block;margin-bottom:2px}
.del{position:absolute;top:5px;right:6px;font:inherit;font-size:10px;background:none;
  border:1px solid currentColor;color:inherit;opacity:.5;border-radius:2px;padding:0 4px;cursor:pointer}
.del:hover{opacity:1}
#stage{width:100%;height:300px;display:block;cursor:grab}
#stage:active{cursor:grabbing}
.hint{padding:6px 12px;border-top:1px solid var(--rule-2);font-size:10.5px;color:var(--ink-3);
  font-family:"IBM Plex Mono",monospace}
.srow,.frow{display:grid;grid-template-columns:auto 1fr auto;gap:9px;align-items:baseline;
  width:100%;text-align:left;background:none;border:0;border-bottom:1px solid var(--rule-2);
  padding:9px 12px;cursor:pointer;color:inherit;font:inherit}
.frow{grid-template-columns:auto 1fr}
.srow:hover,.frow:hover{background:var(--surface-2)}
.srow.sel,.frow.sel{background:var(--accent-soft);box-shadow:inset 3px 0 0 var(--accent)}
.srow:focus-visible,.frow:focus-visible{outline:2px solid var(--accent);outline-offset:-2px}
.sid{font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--ink-3)}
.stext{font-family:"IBM Plex Serif",Georgia,serif}
.smeta{font-size:10.5px;color:var(--ink-3);margin-top:3px}
.chip{font-family:"IBM Plex Mono",monospace;font-size:9.5px;letter-spacing:.06em;padding:2px 6px;
  border-radius:2px;text-transform:uppercase;white-space:nowrap}
.chip.pass{background:var(--pass-soft);color:var(--pass)}
.chip.hold{background:var(--hold-soft);color:var(--hold)}
.chip.adv{background:var(--advisory-soft);color:var(--advisory)}
#faults{display:flex;gap:6px;flex-wrap:wrap;padding:9px 12px;border-bottom:1px solid var(--rule-2)}
button.f,button.reset{font:inherit;font-size:11px;font-family:"IBM Plex Mono",monospace;
  background:var(--surface);border:1px solid var(--rule);color:var(--ink-2);
  padding:4px 8px;border-radius:2px;cursor:pointer}
button.f:hover,button.reset:hover{border-color:var(--accent);color:var(--accent)}
button.f[aria-pressed="true"]{background:var(--hold-soft);border-color:var(--hold);color:var(--hold)}
button.f:focus-visible,button.reset:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
#ledsub{padding:8px 12px 0;font-size:11.5px;color:var(--ink-3)}
.empty{padding:12px;color:var(--pass);font-size:12.5px}
.surrogate{margin-top:14px;border:1px solid var(--advisory);background:var(--advisory-soft);
  padding:8px 11px;border-radius:2px;font-size:12px;color:var(--ink)}
footer{margin-top:16px;padding-top:12px;border-top:1px solid var(--rule);font-size:11px;
  color:var(--ink-3);display:flex;flex-wrap:wrap;gap:8px 24px;justify-content:space-between}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>
"""

BODY = r"""
<div class="wrap">
<header class="top">
  <div>
    <div class="eyebrow">Numberz.ai &middot; RIGLINE &middot; DON26BZ05-NV071</div>
    <h1>SPOKELINE authority loop</h1>
    <p class="sub">The manual on the left is the authority. Everything to the right of it is
    derived. <b>Edit any field in the manual</b> &mdash; the wording, an axis, a travel limit,
    a warning &mdash; and the scenario is rebuilt and re-checked as you type. Click a step, a
    finding, or a part in the model to see the same thing in all three panes.</p>
  </div>
  <div class="kpis" id="kpis"></div>
</header>

<div class="flow">
  <b>Technical manual</b><span>&rarr; extract</span><b>Authority Set</b><span>&rarr; bind to geometry</span>
  <b>Scenario</b><span>&rarr;</span><b>7 checks</b><span>&rarr; SME signs &rarr; export</span>
</div>

<div class="cols">
  <div class="panel">
    <div class="head"><span class="eyebrow">1 &middot; The manual, editable</span>
      <button class="reset" type="button" id="reset">reset to published</button></div>
    <div class="scrollpane" id="manual"></div>
  </div>

  <div>
    <div class="panel">
      <div class="head"><span class="eyebrow">2 &middot; Generated scenario</span>
        <span class="eyebrow">click a part to trace it back</span></div>
      <canvas id="stage"></canvas>
      <div class="hint" id="partnote">drag to orbit &middot; scroll to zoom &middot; click a part</div>
      <div id="scenario"></div>
    </div>
    <div class="surrogate"><b>Surrogate data.</b> Every data module behind this page was
      authored by Numberz.ai and the equipment is a bicycle. The Model Ident Code
      <span class="mono">SPOKE1</span> is fictional. No Navy technical data is used. The
      geometry is a parametric stand-in for photogrammetry; the checks operate on the binding,
      not on the mesh.</div>
  </div>

  <div class="panel">
    <div class="head"><span class="eyebrow">3 &middot; Validation ledger</span><span id="ledstate"></span></div>
    <div id="faults"></div>
    <div id="ledsub"></div>
    <div class="muted" style="padding:4px 12px 8px">Editing the manual changes what is
      <em>correct</em>. The six buttons above leave the manual alone and make the generator
      go wrong instead &mdash; which is the failure the checks exist for.</div>
    <div class="scrollpane" id="ledger"></div>
  </div>
</div>

<footer>
  <span class="mono" id="dist"></span>
  <span>Company-funded &middot; regenerate with <span class="mono">src/run.py</span> and <span class="mono">src/build_viewer.py</span></span>
</footer>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>const D = __DATA__;
const _k=document.querySelector("#kpis"), _m=D.metrics;
[["Detection","%s"],["False positives","%s"],["Faults injected",_m.overall.faults],
 ["Checks","7"]].forEach(function(p){
  var k=document.createElement("div"); k.className="kpi";
  var n=document.createElement("div"); n.className="n"; n.textContent=p[1];
  var l=document.createElement("div"); l.className="l"; l.textContent=p[0];
  k.appendChild(n); k.appendChild(l); _k.appendChild(k);});
document.querySelector("#dist").textContent=Object.values(D.manual.markings)[0]||"";
</script>
<script>__APP__</script>
"""


def main():
    data = payload()
    m = data["metrics"]
    body = BODY.replace("%s", "{:.1f}%".format(m["overall"]["rate"] * 100), 1)
    body = body.replace("%s", "{:.0f}%".format(m["clean_control"]["false_positive_rate"] * 100), 1)
    app = open(os.path.join(HERE, "src", "viewer_app.js"), encoding="utf-8").read()
    html = (HEAD + "</head>\n<body>\n"
            + body.replace("__DATA__", json.dumps(data)).replace("__APP__", app)
            + "</body>\n</html>\n")
    out = os.path.join(HERE, "viewer", "spokeline_viewer.html")
    open(out, "w", encoding="utf-8").write(html)
    print("wrote %s  (%.0f KB)" % (out, os.path.getsize(out) / 1024.0))


if __name__ == "__main__":
    main()
