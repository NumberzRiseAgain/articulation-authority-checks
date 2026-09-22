/* SPOKELINE viewer — the authority loop, live in the browser.
   The manual is the authority. The scenario is derived from it. Edit the manual and the
   scenario is regenerated and re-checked; inject a generator fault and the scenario
   diverges from the manual and the checks catch it. Both paths are the proposal's claim. */
const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
const el = (t,c,x)=>{const n=document.createElement(t); if(c)n.className=c;
  if(x!==undefined)n.textContent=x; return n;};
const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const AXES=["X","Y","Z"], AI={X:0,Y:1,Z:2};

let MAN = structuredClone(D.manual);   // the authority — editable
let INJ = null;                        // generator fault, if any
let SEL = null;                        // selected step id
const BIND = D.binding, SEG = D.segments;

/* ---------- derive the scenario from the manual ---------- */
function derive(){
  const steps = MAN.steps.map((s,i)=>({...structuredClone(s), order:i, generated:false}));
  const sc = {steps};
  if(!INJ) return sc;
  const f = INJ;
  if(f==="F2"){ const s=sc.steps.find(x=>x.id==="stp-030")||sc.steps[0];
    s.travel_start=-(s.travel_start||0); s.travel_end=-(s.travel_end||0);
    s.sense = s.sense==="negative"?"positive":"negative"; s.generated=true; }
  if(f==="F3"){ const s=sc.steps.find(x=>x.id==="stp-010")||sc.steps[0];
    const j=MAN.joints[s.part]; s.travel_end=(j&&j.upper!=null? j.upper:100)*1.6; s.generated=true; }
  if(f==="F4"){ const a=sc.steps.findIndex(x=>x.id==="stp-040"), b=sc.steps.findIndex(x=>x.id==="stp-050");
    if(a>-1&&b>-1){ const t=sc.steps[a].order; sc.steps[a].order=sc.steps[b].order; sc.steps[b].order=t;
      sc.steps[a].generated=sc.steps[b].generated=true; } }
  if(f==="F5"){ const s=sc.steps.find(x=>x.conditions.length); if(s){ s.conditions=s.conditions.slice(1); s.generated=true; } }
  if(f==="F6"){ const base=sc.steps[0];
    sc.steps.push({...structuredClone(base), id:"stp-phantom", order:sc.steps.length,
      text:"Verify accumulator pressure before proceeding.", source:"INVENTED#none",
      conditions:[], generated:true}); }
  if(f==="F1"){ sc.swapBinding=["SPK-1200","SPK-1400"]; }
  return sc;
}
function bindingFor(sc){
  const b={...BIND};
  if(sc.swapBinding){ const [x,y]=sc.swapBinding; const t=b[x]; b[x]=b[y]; b[y]=t; }
  return b;
}

/* ---------- geometry helpers ---------- */
const aabb = seg => { const s=SEG[seg]; return [0,1,2].map(i=>[s.c[i]-s.h[i], s.c[i]+s.h[i]]); };
const NONACT = new Set(D.non_actionable||[]);
const segsOf = (bind,pid)=>{ const v=bind[pid]; if(v==null) return []; return Array.isArray(v)?[...v]:[v]; };
const unionAabb = segs => { const bs=segs.map(aabb);
  return [0,1,2].map(i=>[Math.min(...bs.map(b=>b[i][0])), Math.max(...bs.map(b=>b[i][1]))]); };
const grow = (bx,f=0.25) => bx.map(([lo,hi])=>{const p=(hi-lo)*f; return [lo-p,hi+p];});
const hit = (a,b,tol=0)=>[0,1,2].every(i=>a[i][0]<b[i][1]-tol && b[i][0]<a[i][1]-tol);
function rot(p,piv,ax,deg){const a=deg*Math.PI/180,c=Math.cos(a),s=Math.sin(a);
  let x=p[0]-piv[0],y=p[1]-piv[1],z=p[2]-piv[2];
  if(ax==="X"){[y,z]=[y*c-z*s,y*s+z*c];} else if(ax==="Y"){[x,z]=[x*c+z*s,-x*s+z*c];}
  else {[x,y]=[x*c-y*s,x*s+y*c];}
  return [x+piv[0],y+piv[1],z+piv[2]];}
function swept(seg,motion,ax,a0,a1,n=13){
  const s=SEG[seg], piv=s.pivot||s.c, pts=[];
  const corners=[];
  for(const sx of[-1,1])for(const sy of[-1,1])for(const sz of[-1,1])
    corners.push([s.c[0]+sx*s.h[0], s.c[1]+sy*s.h[1], s.c[2]+sz*s.h[2]]);
  for(let k=0;k<n;k++){ const t=a0+(a1-a0)*k/(n-1);
    for(const p of corners){
      if(motion==="prismatic"){ const q=[...p]; q[AI[ax]]+=t; pts.push(q); }
      else pts.push(rot(p,piv,ax,t)); } }
  return [0,1,2].map(i=>[Math.min(...pts.map(p=>p[i])), Math.max(...pts.map(p=>p[i]))]);
}
function ancestors(pid){const o=[];let c=MAN.parts[pid]&&MAN.parts[pid].parent;
  while(c){o.push(c); c=MAN.parts[c]&&MAN.parts[c].parent;} return o;}

/* ---------- the seven checks, ported from src/checks.py ---------- */
const CW=["clockwise"], CCW=["counter-clockwise","counterclockwise","anti-clockwise"];
function stepClass(s){
  const j=MAN.joints[s.part]; if(!j) return ["extraction",null];
  if(s.motion==="prismatic"&&j.type!=="prismatic") return ["extraction",j];
  if(s.motion==="revolute"&&!["revolute","continuous"].includes(j.type)) return ["extraction",j];
  return ["articulation",j];
}
function runChecks(sc,bind){
  const F=[], add=(c,sev,where,detail)=>F.push({check:c,severity:sev,where,detail});
  // C1. Coverage and identity consistency, ported from checks.c1_coverage_and_identity
  // (3 Sep 12:02 rewrite): not a bijection. (a) every actionable part maps to at least one
  // segment; (b) every actionable segment traces to exactly one part; (c) geometry with no
  // part is allowed only when classified non-actionable; (d) a part's segments sit within its
  // parent's, with the same 25% expansion as the Python.
  const claimed={};
  for(const pid of Object.keys(MAN.parts)){
    const segs=segsOf(bind,pid);
    if(!segs.length){ add("C1","fail",pid,"no geometry segment maps to this actionable part"); continue; }
    for(const sg of segs){
      if(claimed[sg]!==undefined && claimed[sg]!==pid)
        add("C1","fail",pid,`segment ${sg} is claimed by both ${claimed[sg]} and ${pid}`);
      claimed[sg]=pid;
    }
  }
  for(const sg of Object.keys(SEG)){
    if(claimed[sg]!==undefined){
      if(NONACT.has(sg)) add("C1","fail",sg,`segment is classified non-actionable but is bound to ${claimed[sg]}`);
      continue;
    }
    if(!NONACT.has(sg)) add("C1","fail",sg,"geometry segment carries no part and is not classified non-actionable");
  }
  for(const pid of Object.keys(MAN.parts)){
    const par=MAN.parts[pid].parent; if(!par) continue;
    const cs=segsOf(bind,pid), ps=segsOf(bind,par); if(!cs.length||!ps.length) continue;
    if(!hit(grow(unionAabb(ps)), unionAabb(cs)))
      add("C1","fail",pid,`geometry bound to ${pid} does not sit within its parent ${par}`);
  }
  for(const s of sc.steps){
    const [kind,j]=stepClass(s);
    if(kind==="articulation"){
      // C2
      if(s.axis!==j.axis) add("C2","fail",s.id,
        `step turns ${s.part} about ${s.axis}; the manual declares axis ${j.axis}`);
      const t=(s.text||"").toLowerCase();
      let want=null;
      if(CCW.some(w=>t.includes(w))) want="negative"; else if(CW.some(w=>t.includes(w))) want="positive";
      if(want&&s.sense&&s.sense!==want) add("C2","fail",s.id,
        `step text says ${want==="negative"?"counter-clockwise":"clockwise"} but the motion is ${s.sense}`);
      // C3
      if(s.travel_end!=null){
        if(j.lower==null||j.upper==null)
          add("C3","advisory",s.id,`no travel limit stated for ${s.part}; not assumed free`);
        else { const lo=Math.min(j.lower,j.upper), hi=Math.max(j.lower,j.upper);
          for(const v of [s.travel_start,s.travel_end])
            if(v!=null&&(v<lo-1e-6||v>hi+1e-6)) add("C3","fail",s.id,
              `travel ${Math.round(v)} ${s.unit||""} is outside the declared limit ${lo} to ${hi}`);
        }
      }
    }
    // C5
    const g=bind[s.part];
    if(g&&s.travel_end!=null){
      const sw=swept(g,s.motion,s.axis,s.travel_start||0,s.travel_end);
      const rel=new Set(ancestors(s.part));
      for(const pid of Object.keys(MAN.parts)){
        if(pid===s.part||rel.has(pid)||ancestors(pid).includes(s.part)) continue;
        const o=bind[pid]; if(!o||o===g) continue;
        if(hit(sw,aabb(o),1)){ add("C5","fail",s.id,
          `${s.part} cannot travel its stated path without striking ${pid}`); break; }
      }
    }
    // C7
    const known=new Set(MAN.steps.map(x=>x.source));
    if(!known.has(s.source)) add("C7","fail",s.id,"step has no source element in the manual");
    const kc=new Set(MAN.constraints.map(c=>c.source));
    for(const c of s.conditions) if(!kc.has(c.source))
      add("C7","fail",c.id,"annotation has no source element in the manual");
  }
  // C4
  const ord=[...sc.steps].sort((a,b)=>a.order-b.order);
  for(let i=0;i<ord.length;i++) for(let j2=i+1;j2<ord.length;j2++){
    const a=ord[i], b=ord[j2]; if(a.part===b.part) continue;
    if(ancestors(a.part).includes(b.part)) continue;
    if(ancestors(b.part).includes(a.part)) add("C4","fail",b.id,
      `${a.part} is removed at step ${a.id} before its own sub-component ${b.part} at step ${b.id}`);
  }
  // C6
  const attached=new Set();
  for(const s of sc.steps) for(const c of s.conditions) attached.add(c.id+"|"+s.id);
  for(const con of MAN.constraints) if(!attached.has(con.id+"|"+con.step))
    add("C6","fail",con.id,`${con.kind} from the manual is not attached to step ${con.step} in the scenario`);
  return F;
}

/* ---------- render ---------- */
let SC, BD, FIND;
function recompute(){ SC=derive(); BD=bindingFor(SC); FIND=runChecks(SC,BD);
  renderManual(); renderScenario(); renderLedger(); syncScene(); }

function field(val,cls,oninput,opts){
  let n;
  if(opts){ n=el("select","fld "+cls); opts.forEach(o=>{const op=el("option",null,o); op.value=o;
      if(o===val)op.selected=true; n.append(op);}); }
  else { n=el("input","fld "+cls); n.value=val==null?"":val; if(cls.includes("num"))n.type="number"; }
  n.addEventListener("input",e=>{oninput(n.value); recompute();});
  n.addEventListener("click",e=>e.stopPropagation());
  return n;
}

function renderManual(){
  const w=$("#manual"); w.innerHTML="";
  const dm=el("div","dmhead");
  dm.append(el("span","mono",Object.keys(MAN.markings)[0]||""));
  w.append(dm);
  // joints
  const jw=el("details","jgroup"); jw.append(el("summary",null,"Articulation data — declared joints"));
  const jt=el("div","jrows");
  Object.values(MAN.joints).forEach(j=>{
    const r=el("div","jrow"); r.dataset.part=j.part;
    r.append(el("span","mono pid",j.part));
    r.append(el("span","muted",MAN.parts[j.part]?MAN.parts[j.part].name:""));
    r.append(field(j.axis,"ax",v=>{j.axis=v},AXES));
    r.append(el("span","muted",j.type));
    const lo=field(j.lower,"num",v=>{j.lower=v===""?null:+v});
    const hi=field(j.upper,"num",v=>{j.upper=v===""?null:+v});
    r.append(lo,el("span","muted","to"),hi,el("span","muted",j.unit||""));
    jt.append(r);
  });
  jw.append(jt); w.append(jw);
  // steps
  MAN.steps.forEach((s,i)=>{
    const b=el("div","mstep"); b.dataset.step=s.id; b.tabIndex=0;
    if(SEL===s.id) b.classList.add("sel");
    const h=el("div","mhead");
    h.append(el("span","mono sid",s.id));
    h.append(el("span","mono dmc",s.dm.replace("_001-00_EN-US.XML","")));
    b.append(h);
    const ta=el("textarea","fld text"); ta.value=s.text; ta.rows=2;
    ta.addEventListener("input",()=>{s.text=ta.value; recompute();});
    ta.addEventListener("click",e=>e.stopPropagation());
    b.append(ta);
    const at=el("div","attrs");
    at.append(el("span","lab","part"), el("span","mono",s.part));
    at.append(el("span","lab","axis"), field(s.axis,"ax",v=>{s.axis=v},AXES));
    at.append(el("span","lab","sense"), field(s.sense,"ax",v=>{s.sense=v},["positive","negative"]));
    at.append(el("span","lab","travel"), field(s.travel_start,"num",v=>{s.travel_start=+v}),
              el("span","lab","→"), field(s.travel_end,"num",v=>{s.travel_end=+v}),
              el("span","lab",s.unit||""));
    b.append(at);
    s.conditions.forEach((c,ci)=>{
      const n=el("div","notice "+c.kind);
      n.append(el("b",null,c.kind));
      n.append(document.createTextNode(c.text));
      const x=el("button","del","remove from manual"); x.type="button";
      x.title="Removing it from the authority is a legal edit — the scenario simply stops carrying it. Use 'drop a warning' to see the generator lose one instead.";
      x.addEventListener("click",e=>{e.stopPropagation();
        MAN.constraints=MAN.constraints.filter(k=>!(k.id===c.id&&k.step===s.id));
        s.conditions.splice(ci,1); recompute();});
      n.append(x); b.append(n);
    });
    b.addEventListener("click",()=>select(s.id));
    w.append(b);
  });
}

function renderScenario(){
  const w=$("#scenario"); w.innerHTML="";
  const held=new Set(FIND.filter(f=>f.severity==="fail").map(f=>f.where));
  [...SC.steps].sort((a,b)=>a.order-b.order).forEach(s=>{
    const r=el("button","srow"); r.type="button"; r.dataset.step=s.id;
    if(SEL===s.id) r.classList.add("sel");
    r.append(el("span","mono sid",String(s.order+1)));
    const m=el("div");
    m.append(el("div","stext",s.text));
    m.append(el("div","mono smeta",
      `${s.part} · ${s.motion} ${s.axis} · ${Math.round(s.travel_start||0)}→${Math.round(s.travel_end||0)} ${s.unit||""}`));
    r.append(m);
    const st=held.has(s.id)?"hold":"pass";
    r.append(el("span","chip "+st, st==="hold"?"held":"pass"));
    r.addEventListener("click",()=>select(s.id));
    w.append(r);
  });
}

function renderLedger(){
  const b=$("#ledger"); b.innerHTML="";
  const fails=FIND.filter(f=>f.severity==="fail");
  const st=$("#ledstate"); st.className="chip "+(fails.length?"hold":"pass");
  st.textContent=fails.length? fails.length+" held" : "all clear";
  $("#ledsub").textContent = INJ
    ? "A generator fault is active. The manual is untouched; the scenario diverges from it."
    : "The scenario is derived from the manual as it stands. Edit the manual and this re-runs.";
  if(!FIND.length){ b.append(el("div","empty","Nothing to report.")); return; }
  FIND.forEach(f=>{
    const r=el("button","frow"); r.type="button"; r.dataset.step=f.where;
    r.append(el("span","chip "+(f.severity==="fail"?"hold":"adv"),f.check));
    const m=el("div"); m.append(el("div",null,f.detail));
    m.append(el("div","mono smeta","at "+f.where));
    r.append(m);
    r.addEventListener("click",()=>select(f.where));
    b.append(r);
  });
}

function select(id){
  SEL=id;
  $$(".mstep,.srow,.frow").forEach(n=>n.classList.toggle("sel", n.dataset.step===id));
  const m=$(`.mstep[data-step="${id}"]`); if(m) m.scrollIntoView({block:"nearest",behavior:"smooth"});
  const s=SC.steps.find(x=>x.id===id); if(s) play(s);
  syncScene();
}

/* ---------- 3D, optional ----------
   The model is additive. If three.js does not load, or WebGL is unavailable, every other
   pane still works: the manual stays editable and the checks still run. */
const cv=$("#stage");
const HAS3D = (typeof THREE!=="undefined") && (()=>{ try{
  return !!document.createElement("canvas").getContext("webgl"); }catch(e){ return false; } })();
let renderer,scene,camera,root,ray,ndc;
const nodes={},mats={};
if(HAS3D){
renderer=new THREE.WebGLRenderer({canvas:cv,antialias:true,alpha:true});
scene=new THREE.Scene(); camera=new THREE.PerspectiveCamera(38,2,.05,60);
root=new THREE.Group(); scene.add(root);
scene.add(new THREE.HemisphereLight(0xffffff,0x223344,1.15));
const dl=new THREE.DirectionalLight(0xffffff,.75); dl.position.set(2,4,3); scene.add(dl);
Object.entries(BIND).forEach(([pid,seg])=>{
  const s=SEG[seg], piv=s.pivot||s.c;
  const g=new THREE.BoxGeometry(s.h[0]*2/1000,s.h[1]*2/1000,s.h[2]*2/1000);
  g.translate((s.c[0]-piv[0])/1000,(s.c[1]-piv[1])/1000,(s.c[2]-piv[2])/1000);
  const m=new THREE.MeshLambertMaterial({color:new THREE.Color(css("--ink-3"))});
  const mesh=new THREE.Mesh(g,m);
  mesh.position.set(piv[0]/1000,piv[1]/1000,piv[2]/1000);
  mesh.userData.pid=pid;
  mesh.add(new THREE.LineSegments(new THREE.EdgesGeometry(g),
    new THREE.LineBasicMaterial({color:new THREE.Color(css("--ink")),transparent:true,opacity:.28})));
  root.add(mesh); nodes[pid]=mesh; mats[pid]=m;
});
root.position.y=-0.55;
ray=new THREE.Raycaster(); ndc=new THREE.Vector2();
} else {
  cv.style.display="none";
  const hint=$("#partnote"); if(hint) hint.style.display="none";
  const n=document.createElement("div"); n.className="hint";
  n.textContent="3-D model unavailable in this browser. The manual, the scenario and the checks all still work.";
  cv.parentNode.insertBefore(n,cv.nextSibling);
}

function syncScene(){
  if(!HAS3D) return;
  const held=new Set(FIND.filter(f=>f.severity==="fail").map(f=>f.where));
  const heldParts=new Set();
  held.forEach(w=>{ const s=SC.steps.find(x=>x.id===w); if(s)heldParts.add(s.part); if(mats[w])heldParts.add(w); });
  const sel=SC.steps.find(x=>x.id===SEL);
  Object.entries(mats).forEach(([pid,m])=>{
    if(sel&&sel.part===pid) m.color.set(css("--accent"));
    else if(heldParts.has(pid)) m.color.set(css("--hold"));
    else m.color.set(css("--ink-3"));
  });
}
let anim=null;
function play(s){
  if(!HAS3D) return;
  const mesh=nodes[s.part]; if(!mesh) return;
  const seg=SEG[BD[s.part]], piv=seg.pivot||seg.c;
  const a0=s.travel_start||0,a1=s.travel_end||0,ax=s.axis,t0=performance.now();
  anim=t=>{ let k=Math.min(1,(t-t0)/1100); k=k<.5?2*k*k:1-Math.pow(-2*k+2,2)/2;
    const v=a0+(a1-a0)*k;
    mesh.rotation.set(0,0,0); mesh.position.set(piv[0]/1000,piv[1]/1000,piv[2]/1000);
    if(s.motion==="prismatic"){ const p=[piv[0]/1000,piv[1]/1000,piv[2]/1000]; p[AI[ax]]+=v/1000;
      mesh.position.set(p[0],p[1],p[2]); }
    else { const r=v*Math.PI/180;
      if(ax==="X")mesh.rotation.x=r; else if(ax==="Y")mesh.rotation.y=r; else mesh.rotation.z=r; }
    return k<1; };
}
cv.addEventListener("click",e=>{
  if(!HAS3D) return;
  const r=cv.getBoundingClientRect();
  ndc.x=((e.clientX-r.left)/r.width)*2-1; ndc.y=-((e.clientY-r.top)/r.height)*2+1;
  ray.setFromCamera(ndc,camera);
  const h=ray.intersectObjects(root.children,false);
  if(!h.length) return;
  const pid=h[0].object.userData.pid;
  const s=[...SC.steps].sort((a,b)=>a.order-b.order).find(x=>x.part===pid);
  if(s) select(s.id);
  else { $("#partnote").textContent = pid+" — "+(MAN.parts[pid]?MAN.parts[pid].name:"")+
    ": no procedural step in this manual drives this part."; }
});
let yaw=-.62,pitch=.2,dist=3.05,drag=null,moved=false;
cv.addEventListener("pointerdown",e=>{drag={x:e.clientX,y:e.clientY};moved=false;cv.setPointerCapture(e.pointerId)});
cv.addEventListener("pointermove",e=>{ if(!drag)return; moved=true;
  yaw+=(e.clientX-drag.x)*.008; pitch=Math.max(-1.2,Math.min(1.2,pitch+(e.clientY-drag.y)*.006));
  drag={x:e.clientX,y:e.clientY};});
addEventListener("pointerup",()=>drag=null);
cv.addEventListener("wheel",e=>{e.preventDefault();dist=Math.max(1.5,Math.min(7,dist+e.deltaY*.0022))},{passive:false});
function frame(t){
  if(!HAS3D) return;
  const w=cv.clientWidth,h=cv.clientHeight;
  if(cv.width!==w*devicePixelRatio||cv.height!==h*devicePixelRatio){
    renderer.setPixelRatio(devicePixelRatio); renderer.setSize(w,h,false);
    camera.aspect=w/h; camera.updateProjectionMatrix(); }
  camera.position.set(Math.sin(yaw)*Math.cos(pitch)*dist,Math.sin(pitch)*dist+.15,Math.cos(yaw)*Math.cos(pitch)*dist);
  camera.lookAt(0,.1,.35);
  if(anim&&!anim(t)) anim=null;
  renderer.render(scene,camera); requestAnimationFrame(frame);
}

/* ---------- controls ---------- */
const FAULTS=[["F1","swap two parts"],["F2","reverse a direction"],["F3","exceed a limit"],
  ["F4","transpose two steps"],["F5","drop a warning"],["F6","invent a step"]];
FAULTS.forEach(([k,label])=>{
  const b=el("button","f"); b.type="button"; b.textContent=label;
  b.setAttribute("aria-pressed","false"); b.dataset.f=k;
  b.addEventListener("click",()=>{ INJ = INJ===k?null:k;
    $$("#faults .f").forEach(x=>x.setAttribute("aria-pressed",String(x.dataset.f===INJ)));
    recompute(); });
  $("#faults").append(b);
});
$("#reset").addEventListener("click",()=>{ MAN=structuredClone(D.manual); INJ=null; SEL=null;
  $$("#faults .f").forEach(x=>x.setAttribute("aria-pressed","false")); recompute(); });

recompute(); select(MAN.steps[0].id); if(HAS3D) requestAnimationFrame(frame);
