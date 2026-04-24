import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from simulation.simulation_engine       import Simulation, Building, Patient, Staff
from decision.decision_engine           import run_decision_engine
from decision.gemma_decision_engine     import run_decision_engine_gemma
from assignment.assignment_engine       import run_assignment
from verification.verification_engine   import VerificationEngine
from planner.simulation_planner         import run_planner
from firefighter.firefighter_module     import get_firefighter_briefing

# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="CrisisAI", layout="wide",
                   initial_sidebar_state="expanded")

# ─────────────────────────── CSS ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600&display=swap');
html,[class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background:#090d17;}
.block-container{padding:1.2rem 1.8rem 2rem!important;max-width:100%!important;}
button[data-testid="baseButton-primary"]{
  background:linear-gradient(135deg,#ef4444,#b91c1c)!important;
  border:none!important;color:#fff!important;font-weight:700!important;}
button[data-testid="baseButton-secondary"]{
  background:#151c2c!important;border:1px solid #2a3348!important;
  color:#cbd5e1!important;font-weight:600!important;}

/* header */
.hdr{background:linear-gradient(135deg,#0f1629 0%,#0a0f1e 100%);
     border:1px solid #1e2a40;border-radius:14px;padding:18px 26px;
     margin-bottom:16px;display:flex;align-items:center;justify-content:space-between;}
.hdr-title{font-size:20px;font-weight:900;color:#f1f5f9;letter-spacing:-.3px;}
.hdr-sub{font-size:12px;color:#475569;margin-top:3px;}
.hdr-badges{display:flex;gap:8px;align-items:center;}
.badge-live{background:#ef4444;color:#fff;font-size:10px;font-weight:800;
            padding:3px 10px;border-radius:20px;letter-spacing:1px;
            animation:pulse 1.6s infinite;}
.badge-tick{background:#1e2a40;color:#94a3b8;font-size:11px;font-weight:700;
            padding:4px 12px;border-radius:20px;font-family:'JetBrains Mono';}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.55}}

/* stat cards */
.stats{display:flex;gap:10px;margin-bottom:16px;}
.sc{flex:1;background:#0f1629;border:1px solid #1e2a40;border-radius:11px;
    padding:13px 16px;}
.sc-label{font-size:10px;color:#475569;font-weight:700;letter-spacing:.8px;
          text-transform:uppercase;}
.sc-val{font-size:26px;font-weight:900;margin-top:3px;line-height:1;}
.sc-sub{font-size:11px;color:#475569;margin-top:2px;}
.fire{color:#ef4444}.warn{color:#f97316}.ok{color:#22c55e}
.blue{color:#3b82f6}.purple{color:#a855f7}.yellow{color:#eab308}

/* section label */
.slabel{font-size:10px;font-weight:800;color:#475569;letter-spacing:1.5px;
        text-transform:uppercase;margin-bottom:8px;padding-bottom:5px;
        border-bottom:1px solid #1a2235;}

/* grid */
.gwrap{background:#0c1120;border:1px solid #1e2a40;border-radius:12px;
       padding:14px;overflow-x:auto;}
.grow{display:flex;gap:2px;margin-bottom:2px;}
.gc{width:42px;height:42px;border-radius:5px;display:flex;align-items:center;
    justify-content:center;font-size:16px;position:relative;border:1px solid transparent;
    flex-shrink:0;}
.gc-empty {background:#111827;border-color:#1f2937;}
.gc-fire  {background:#3b0a0a;border-color:#ef4444;box-shadow:0 0 7px #ef444455;}
.gc-pred  {background:#2d2000;border-color:#eab308;box-shadow:0 0 4px #eab30840;}
.gc-smoke {background:#1f1500;border-color:#92400e;}
.gc-icu   {background:#0a1e3b;border-color:#3b82f6;box-shadow:0 0 6px #3b82f640;}
.gc-mob   {background:#082018;border-color:#22c55e;}
.gc-staff {background:#1a0a3b;border-color:#a855f7;box-shadow:0 0 5px #a855f740;}
.gc-exit  {background:#1a2a1a;border-color:#4ade80;}
.gc-ff    {background:#1a1000;border-color:#f59e0b;box-shadow:0 0 8px #f59e0b60;}
.coord{font-size:6px;color:#374151;position:absolute;bottom:1px;right:2px;
       font-family:'JetBrains Mono';}
.legend{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px;}
.li{display:flex;align-items:center;gap:5px;font-size:10px;color:#6b7280;}
.ld{width:10px;height:10px;border-radius:3px;}

/* priority cards */
.pcard{background:#0f1629;border-radius:9px;padding:11px 14px;margin-bottom:7px;
       display:flex;align-items:center;justify-content:space-between;
       border-left:4px solid;border-top:1px solid #1e2a40;
       border-right:1px solid #1e2a40;border-bottom:1px solid #1e2a40;}
.pname{font-weight:700;font-size:13px;color:#e2e8f0;}
.pmeta{font-size:10px;color:#475569;margin-top:2px;}
.pscore{font-size:20px;font-weight:900;font-family:'JetBrains Mono';}
.badge{font-size:9px;font-weight:800;padding:2px 8px;border-radius:20px;
       margin-left:6px;letter-spacing:.4px;}
.bc{background:#3b0a0a;color:#ef4444;border:1px solid #ef444440;}
.bh{background:#3b1500;color:#f97316;border:1px solid #f9731640;}
.bm{background:#1a2a00;color:#84cc16;border:1px solid #84cc1640;}
.bl{background:#1a2535;color:#64748b;border:1px solid #47556940;}

/* assignment cards */
.acard{background:#0f1629;border:1px solid #1e2a40;border-radius:9px;
       padding:12px 14px;margin-bottom:7px;}
.afrom{font-size:12px;font-weight:800;color:#a855f7;font-family:'JetBrains Mono';}
.aarrow{font-size:14px;color:#374151;}
.ato{font-size:12px;font-weight:800;color:#3b82f6;font-family:'JetBrains Mono';}
.adetail{font-size:10px;color:#475569;margin-top:4px;}
.aroom{background:#1a2235;color:#94a3b8;font-size:10px;font-family:'JetBrains Mono';
       padding:2px 7px;border-radius:4px;display:inline-block;margin-top:3px;}
.aroute-ok  {font-size:11px;color:#22c55e;margin-top:4px;}
.aroute-warn{font-size:11px;color:#f97316;margin-top:4px;}

/* plan cards */
.plan-card{border-radius:12px;padding:16px 18px;margin-bottom:10px;
           border:2px solid;transition:all .2s;}
.plan-rec {border-color:#22c55e;background:linear-gradient(135deg,#082018,#051510);}
.plan-norm{border-color:#1e2a40;background:#0f1629;}
.plan-name{font-size:15px;font-weight:800;color:#f1f5f9;}
.plan-desc{font-size:12px;color:#64748b;margin-top:4px;}
.plan-surv{font-size:32px;font-weight:900;font-family:'JetBrains Mono';}
.plan-trade{font-size:11px;color:#64748b;margin-top:6px;font-style:italic;}
.rec-badge{background:#22c55e;color:#000;font-size:10px;font-weight:800;
           padding:3px 10px;border-radius:20px;margin-left:8px;}

/* verification table */
.vtask{background:#0f1629;border:1px solid #1e2a40;border-radius:8px;
       padding:10px 13px;margin-bottom:6px;display:flex;
       align-items:center;justify-content:space-between;}
.vstatus-active    {color:#3b82f6;font-weight:700;font-size:11px;}
.vstatus-complete  {color:#22c55e;font-weight:700;font-size:11px;}
.vstatus-failed    {color:#ef4444;font-weight:700;font-size:11px;}
.vstatus-likely    {color:#84cc16;font-weight:700;font-size:11px;}
.conf-bar{height:4px;border-radius:4px;background:#1e2a40;width:80px;margin-top:3px;}
.conf-fill{height:4px;border-radius:4px;}

/* FF panel */
.ff-brief{background:linear-gradient(135deg,#1a1000,#0d0a00);
          border:1px solid #f59e0b50;border-radius:12px;padding:18px 20px;
          margin-bottom:14px;}
.ff-title{font-size:16px;font-weight:800;color:#f59e0b;}
.ff-line{font-size:13px;color:#92400e;margin-top:5px;line-height:1.7;}
.ff-entry{background:#1a2a10;border:1px solid #22c55e40;border-radius:8px;
          padding:10px 14px;margin-bottom:8px;}
.ff-zone{background:#2d0a0a;border:1px solid #ef444440;border-radius:8px;
         padding:10px 14px;margin-bottom:8px;}
.ff-patient{background:#0a1e3b;border:1px solid #3b82f640;border-radius:8px;
            padding:10px 14px;margin-bottom:8px;}

/* formula box */
.formula{background:#0f1629;border:1px solid #2a3a5c;border-radius:10px;
         padding:14px 18px;font-family:'JetBrains Mono';font-size:13px;
         color:#93c5fd;margin-bottom:12px;text-align:center;}
.formula .var{color:#f472b6;}.formula .eq{color:#e2e8f0;font-size:15px;font-weight:700;}

/* reasoning box */
.reasoning{background:#0a1e0a;border:1px solid #166534;border-radius:10px;
           padding:14px 16px;font-size:13px;color:#4ade80;
           line-height:1.6;margin-top:12px;}

/* log */
.logbox{background:#050810;border:1px solid #131d30;border-radius:8px;
        padding:8px 12px;font-family:'JetBrains Mono';font-size:10px;
        color:#475569;max-height:130px;overflow-y:auto;}

[data-testid="stSidebar"]{background:#090d17!important;border-right:1px solid #1a2235!important;}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────── Session state ───────────────────────────────────
def _init():
    defaults = {
        "sim":               None,
        "verifier":          None,
        "decisions":         [],
        "assignments":       {"assignments": []},
        "verification":      {},
        "plan":              None,
        "ff_briefing":       None,
        "log":               [],
        "ff_joined":         False,
        "initialized":       False,
        "ai_fire_direction": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
_init()


# ─────────────────────────── Build simulation ────────────────────────────────
def build_simulation():
    building = Building(10, 10)
    patients = [
        Patient(0, 9, 2, movable=True,  condition="stable"),
        Patient(1, 2, 7, movable=False, condition="critical"),  # ICU
        Patient(2, 1, 7, movable=True,  condition="stable"),
        Patient(3, 8, 2, movable=False, condition="critical"),  # ICU
        Patient(4, 6, 2, movable=False, condition="stable"),    # ICU
    ]
    staff = [
        Staff(0, 2, 4, trained=True,  role="medic"),
        Staff(1, 5, 5, trained=False, role="nurse"),
        Staff(2, 7, 5, trained=True,  role="medic"),
    ]
    return Simulation(building, patients, staff), VerificationEngine(deadline_ticks=3)


def do_tick():
    sim   = st.session_state.sim
    verif = st.session_state.verifier

    sim.update_fire()

    # ── Gemma 4-enhanced decision engine ──────────────────────────────────────
    gemma_result = run_decision_engine_gemma(sim)
    decisions    = gemma_result["decisions"]
    ai_direction = gemma_result["ai_fire_direction"]

    assignments  = run_assignment(sim, decisions)
    verif.register_assignments(assignments, sim.tick)
    verification = verif.verify_tick(sim, sim.tick)
    plan         = run_planner(sim)
    ff_briefing  = get_firefighter_briefing(sim)

    # Handle reassignments from verification failures
    if verification.get("reassign_needed"):
        st.session_state.log.append(
            f"[Tick {sim.tick}] ⚠️ REASSIGN: "
            + ", ".join(r["reason"] for r in verification["reassign_needed"])
        )

    st.session_state.decisions        = decisions
    st.session_state.assignments      = assignments
    st.session_state.verification     = verification
    st.session_state.plan             = plan
    st.session_state.ff_briefing      = ff_briefing
    st.session_state.ai_fire_direction = ai_direction

    vcounts = verif.summary()
    st.session_state.log.append(
        f"[Tick {sim.tick}] 🔥 {len(sim.fire)} fire cells | "
        f"👷 {len(assignments['assignments'])} assigned | "
        f"✅ {vcounts['completed']+vcounts['likely_complete']} complete | "
        f"❌ {vcounts['failed']} failed"
    )


# ─────────────────────────── Grid renderer ───────────────────────────────────
def render_grid(sim, predicted_fire=None):
    predicted_set = set(predicted_fire) if predicted_fire else set()
    fire_set   = set(sim.fire)
    pat_pos    = {(p.x, p.y): p for p in sim.patients}
    staff_pos  = {(s.x, s.y): s for s in sim.staff}
    ff_pos     = {(f.x, f.y): f for f in sim.firefighters}
    exits      = set(sim.building.exits)

    html = '<div class="gwrap"><div>'
    for y in range(sim.building.height):
        html += '<div class="grow">'
        for x in range(sim.building.width):
            pos = (x, y)
            # Layered priority: fire > FF > staff > patient > predicted > smoke > exit > empty
            if pos in fire_set:
                sev  = sim.fire_severity.get(pos, 1)
                icon = "🔥" if sev >= 3 else "⚠️"
                cls  = "gc-fire"
            elif pos in ff_pos:
                icon = "🚒"; cls = "gc-ff"
            elif pos in staff_pos:
                s = staff_pos[pos]
                icon = "💊" if s.trained else "👷"
                cls  = "gc-staff"
            elif pos in pat_pos:
                p = pat_pos[pos]
                icon = "🏥" if not p.movable else "🧍"
                cls  = "gc-icu" if not p.movable else "gc-mob"
            elif pos in predicted_set:
                icon = "⚠️"; cls = "gc-pred"
            elif sim.smoke_map[y][x] > 0.35:
                icon = "💨"; cls = "gc-smoke"
            elif pos in exits:
                icon = "🚪"; cls = "gc-exit"
            else:
                icon = ""; cls = "gc-empty"

            html += f'<div class="gc {cls}" title="{x},{y}">{icon}<span class="coord">{x},{y}</span></div>'
        html += '</div>'

    html += '''</div>
    <div class="legend">
      <div class="li"><div class="ld" style="background:#ef4444"></div>Fire</div>
      <div class="li"><div class="ld" style="background:#eab308"></div>Predicted fire</div>
      <div class="li"><div class="ld" style="background:#92400e"></div>Smoke</div>
      <div class="li"><div class="ld" style="background:#3b82f6"></div>ICU Patient</div>
      <div class="li"><div class="ld" style="background:#22c55e"></div>Mobile Patient</div>
      <div class="li"><div class="ld" style="background:#a855f7"></div>Staff</div>
      <div class="li"><div class="ld" style="background:#f59e0b"></div>Firefighter</div>
      <div class="li"><div class="ld" style="background:#4ade80"></div>Exit</div>
    </div></div>'''
    return html


# ─────────────────────────── Priority renderer ───────────────────────────────
def render_priorities(decisions, patients):
    mob_map = {p.id: p.movable for p in patients}
    cc  = {"critical":"#ef4444","high":"#f97316","medium":"#84cc16","low":"#475569"}
    bcl = {"critical":"bc","high":"bh","medium":"bm","low":"bl"}
    html = ""
    max_s = max((d["priority"] for d in decisions), default=1) or 1
    for d in decisions:
        pid   = d["patient_id"]; s = d["priority"]
        lvl   = d["explanation"]["priority_level"]
        mob   = "Mobile" if mob_map.get(pid, True) else "ICU — Immobile"
        c     = cc.get(lvl, "#475569")
        pct   = int(s/max_s*100)
        ff    = d.get("predicted_fire_nearby")
        warn  = ' <span style="color:#eab308;font-size:10px">⚠️ predicted fire</span>' if ff else ""
        html += f"""
        <div class="pcard" style="border-left-color:{c}">
          <div>
            <div class="pname">Patient {pid}
              <span class="badge {bcl.get(lvl,'bl')}">{lvl.upper()}</span>{warn}
            </div>
            <div class="pmeta">{mob}</div>
            <div style="height:3px;background:#1a2235;border-radius:3px;
                        margin-top:7px;width:140px">
              <div style="height:3px;background:{c};border-radius:3px;width:{pct}%"></div>
            </div>
          </div>
          <div class="pscore" style="color:{c}">{s}</div>
        </div>"""
    return html


# ─────────────────────────── Assignment renderer ─────────────────────────────
def render_assignments(assignments_data):
    html = ""
    for a in assignments_data.get("assignments", []):
        note = a.get("route_note","")
        ncls = "aroute-ok" if "✅" in note else "aroute-warn"
        bd   = a.get("cost_breakdown",{})
        html += f"""
        <div class="acard">
          <div style="display:flex;align-items:center;gap:8px">
            <span class="afrom">STAFF {a['staff_id']}</span>
            <span class="aarrow">⟶</span>
            <span class="ato">PATIENT {a['patient_id']}</span>
          </div>
          <div class="aroom">→ Room {a['target_room']}</div>
          <div class="adetail" style="margin-top:5px">
            dist={bd.get('distance','?')} | risk={bd.get('path_risk','?')} |
            skill bonus={bd.get('skill_bonus','0')} | cost={bd.get('total_cost','?')}
          </div>
          <div class="{ncls}">{note}</div>
        </div>"""
    if not assignments_data.get("assignments"):
        html = '<div style="color:#475569;font-size:13px;padding:12px">No assignments yet — run a tick.</div>'
    return html


# ─────────────────────────── Sidebar ─────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-size:17px;font-weight:900;color:#f1f5f9;margin-bottom:2px">⚡ CrisisAI</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:11px;color:#475569;margin-bottom:18px">Control Panel</div>', unsafe_allow_html=True)

    if st.button("🚀  Initialize System", use_container_width=True, type="primary"):
        sim, verif = build_simulation()
        st.session_state.sim         = sim
        st.session_state.verifier    = verif
        st.session_state.decisions   = []
        st.session_state.assignments = {"assignments": []}
        st.session_state.verification = {}
        st.session_state.plan        = None
        st.session_state.ff_briefing = None
        st.session_state.log         = ["[Init] System initialized. Fire detected at (5,6). Press 'Next Tick' to begin."]
        st.session_state.ff_joined   = False
        st.session_state.initialized = True
        st.rerun()

    st.markdown("---")

    if st.session_state.initialized:
        if st.button("⏭️  Next Tick", use_container_width=True):
            do_tick()
            st.rerun()

        if st.button("⏩  Run 3 Ticks", use_container_width=True):
            for _ in range(3):
                do_tick()
            st.rerun()

        st.markdown("---")
        ff_label = "🚒  Firefighters Arrived!" if st.session_state.ff_joined else "🚒  Firefighters Arrive"
        if st.button(ff_label, use_container_width=True,
                     disabled=st.session_state.ff_joined):
            sim = st.session_state.sim
            # Add 2 firefighters at safe entry points
            entries = sim.get_safe_entry_points()
            for i, (ex, ey) in enumerate(entries[:2]):
                sim.add_firefighter(ex, ey)
            st.session_state.ff_joined   = True
            st.session_state.ff_briefing = get_firefighter_briefing(sim)
            st.session_state.log.append(
                f"[Tick {sim.tick}] 🚒 Firefighters joined at {entries[:2]}"
            )
            st.rerun()

        st.markdown("---")
        st.markdown("**Simulation Info**")
        if st.session_state.sim:
            sim = st.session_state.sim
            st.markdown(f'<div style="font-size:12px;color:#64748b;line-height:2">'
                        f'Tick: <b style="color:#94a3b8">{sim.tick}</b><br>'
                        f'Fire cells: <b style="color:#ef4444">{len(sim.fire)}</b><br>'
                        f'Patients: <b style="color:#94a3b8">{len(sim.patients)}</b><br>'
                        f'Staff: <b style="color:#a855f7">{len(sim.staff)}</b><br>'
                        f'Firefighters: <b style="color:#f59e0b">{len(sim.firefighters)}</b>'
                        f'</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size:12px;color:#475569">Press Initialize to start.</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="font-size:10px;color:#334155;line-height:1.8">
    🔥 Fire spreads each tick<br>
    ⚠️ Yellow = predicted fire (3 ticks)<br>
    🏥 ICU = immobile, high priority<br>
    💊 Trained medic = ICU specialist<br>
    ✅ Verification tracks task completion<br>
    🎯 Planner compares 3 response plans
    </div>""", unsafe_allow_html=True)


# ─────────────────────────── Header ──────────────────────────────────────────
tick_val = st.session_state.sim.tick if st.session_state.sim else 0
st.markdown(f"""
<div class="hdr">
  <div>
    <div class="hdr-title">🔥 AI-Based Real-Time Crisis Orchestration System</div>
    <div class="hdr-sub">Multi-Occupancy Buildings · Detection → Decision → Assignment → Verification · Firefighter Integration</div>
  </div>
  <div class="hdr-badges">
    <span class="badge-tick">TICK {tick_val:03d}</span>
    <span class="badge-live">LIVE</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────── Stat bar ────────────────────────────────────────
sim   = st.session_state.sim
vcnt  = st.session_state.verifier.summary() if st.session_state.verifier else {}
decs  = st.session_state.decisions
asns  = st.session_state.assignments

fire_n    = len(sim.fire) if sim else 0
crit_n    = sum(1 for d in decs if d["explanation"]["priority_level"] == "critical")
asgn_n    = len(asns.get("assignments", []))
comp_n    = vcnt.get("completed",0) + vcnt.get("likely_complete",0)
fail_n    = vcnt.get("failed",0)
top_score = decs[0]["priority"] if decs else 0
top_pid   = decs[0]["patient_id"] if decs else "-"

st.markdown(f"""
<div class="stats">
  <div class="sc"><div class="sc-label">🔥 Fire Cells</div>
    <div class="sc-val fire">{fire_n}</div><div class="sc-sub">active zones</div></div>
  <div class="sc"><div class="sc-label">⚠️ Critical</div>
    <div class="sc-val warn">{crit_n}</div><div class="sc-sub">patients</div></div>
  <div class="sc"><div class="sc-label">✅ Assigned</div>
    <div class="sc-val ok">{asgn_n}</div><div class="sc-sub">staff deployed</div></div>
  <div class="sc"><div class="sc-label">📋 Completed</div>
    <div class="sc-val blue">{comp_n}</div><div class="sc-sub">tasks verified</div></div>
  <div class="sc"><div class="sc-label">❌ Failed</div>
    <div class="sc-val fire">{fail_n}</div><div class="sc-sub">reassign needed</div></div>
  <div class="sc"><div class="sc-label">🏆 Top Score</div>
    <div class="sc-val purple">{top_score}</div><div class="sc-sub">Patient {top_pid}</div></div>
  <div class="sc"><div class="sc-label">🕒 Tick</div>
    <div class="sc-val yellow">{tick_val}</div><div class="sc-sub">elapsed</div></div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────── Tabs ────────────────────────────────────────────
if not st.session_state.initialized:
    st.markdown("""
    <div style="text-align:center;padding:60px 20px;color:#334155">
      <div style="font-size:48px;margin-bottom:16px">🔥</div>
      <div style="font-size:18px;font-weight:700;color:#475569">System Not Initialized</div>
      <div style="font-size:13px;margin-top:8px">Press <b>Initialize System</b> in the sidebar to begin.</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️  Live Map",
    "🧠  Decision Engine",
    "🎯  AI Planner",
    "✅  Verification",
    "🚒  Firefighter Mode",
])


# ══════════════ TAB 1 — LIVE MAP ═════════════════════════════════════════════
with tab1:
    c1, c2 = st.columns([3, 2], gap="medium")

    with c1:
        st.markdown('<div class="slabel">Building Floor Map</div>', unsafe_allow_html=True)
        if sim:
            predicted = sim.predict_fire_spread(3) if sim.fire else []
            st.markdown(render_grid(sim, predicted), unsafe_allow_html=True)
        else:
            st.info("Initialize system to see map.")

    with c2:
        st.markdown('<div class="slabel">Priority Decisions</div>', unsafe_allow_html=True)
        if decs:
            st.markdown(render_priorities(decs, sim.patients), unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#334155;font-size:13px;padding:10px">Run a tick to see priorities.</div>', unsafe_allow_html=True)

        st.markdown('<div class="slabel" style="margin-top:14px">Staff Assignments</div>', unsafe_allow_html=True)
        st.markdown(render_assignments(asns), unsafe_allow_html=True)

    # Event log
    st.markdown('<div class="slabel" style="margin-top:10px">Event Log</div>', unsafe_allow_html=True)
    log_lines = st.session_state.log[-15:]
    log_html  = "".join(
        f'<div style="margin-bottom:2px;color:{"#ef4444" if "REASSIGN" in l else "#22c55e" if "joined" in l else "#475569"}">{l}</div>'
        for l in reversed(log_lines)
    )
    st.markdown(f'<div class="logbox">{log_html}</div>', unsafe_allow_html=True)


# ══════════════ TAB 2 — DECISION ENGINE ═══════════════════════════════════════
with tab2:

    # ── Gemma 4 AI Fire Analysis Panel ─────────────────────────────────────────
    ai_dir = st.session_state.get("ai_fire_direction", "")
    if ai_dir:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0a1a0a,#051005);
                    border:1px solid #22c55e50;border-radius:12px;
                    padding:16px 20px;margin-bottom:16px;">
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
            <span style="font-size:18px">🤖</span>
            <span style="font-size:13px;font-weight:800;color:#22c55e;letter-spacing:.5px">
              GEMMA 4 — AI FIRE ANALYSIS
            </span>
            <span style="background:#22c55e20;color:#22c55e;font-size:9px;font-weight:800;
                         padding:2px 8px;border-radius:20px;border:1px solid #22c55e40">
              LIVE
            </span>
          </div>
          <div style="font-size:13px;color:#86efac;line-height:1.7;font-style:italic">
            {ai_dir}
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:#0a1020;border:1px solid #1e2a40;border-radius:12px;
                    padding:14px 20px;margin-bottom:16px;display:flex;align-items:center;gap:10px">
          <span style="font-size:16px">🤖</span>
          <span style="font-size:12px;color:#334155">
            Gemma 4 fire analysis will appear after the first tick.
            Set <code>GEMINI_API_KEY</code> env var to enable live AI predictions.
          </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="slabel">Priority Scoring Formula</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="formula">
      <span class="eq">P</span> &nbsp;=&nbsp;
      <span class="var">w₁</span>·<span class="eq">Risk</span> &nbsp;+&nbsp;
      <span class="var">w₂</span>·<span class="eq">Immobility</span> &nbsp;+&nbsp;
      <span class="var">w₃</span>·<span class="eq">Urgency</span> &nbsp;−&nbsp;
      <span class="var">w₄</span>·<span class="eq">NearbyHelp</span>
      <br><br>
      <span style="color:#64748b;font-size:11px">
        w₁=1.2 (risk) &nbsp;|&nbsp; w₂=1.5 (immobility) &nbsp;|&nbsp;
        w₃=1.0 (urgency) &nbsp;|&nbsp; w₄=0.8 (nearby help)
      </span>
    </div>
    """, unsafe_allow_html=True)

    if decs:
        st.markdown('<div class="slabel">Score Breakdown per Patient</div>', unsafe_allow_html=True)
        for d in decs:
            e   = d["explanation"]
            lvl = e["priority_level"]
            cc  = {"critical":"#ef4444","high":"#f97316","medium":"#84cc16","low":"#475569"}
            c   = cc.get(lvl, "#475569")
            icu = "🏥 ICU" if d["is_icu"] else "🧍 Mobile"
            pfw = "⚠️ Predicted fire nearby" if d["predicted_fire_nearby"] else "✅ No predicted threat"
            st.markdown(f"""
            <div style="background:#0f1629;border:1px solid #1e2a40;border-left:4px solid {c};
                        border-radius:9px;padding:12px 16px;margin-bottom:8px">
              <div style="display:flex;justify-content:space-between;align-items:center">
                <span style="font-weight:800;color:#e2e8f0;font-size:14px">
                  Patient {d['patient_id']} — {icu}
                  <span style="font-size:10px;color:{c};margin-left:8px">{lvl.upper()}</span>
                </span>
                <span style="font-family:'JetBrains Mono';font-size:22px;font-weight:900;color:{c}">
                  {d['priority']}
                </span>
              </div>
              <div style="display:flex;gap:12px;margin-top:10px;flex-wrap:wrap">
                <div style="background:#1a2235;border-radius:6px;padding:6px 10px;min-width:100px">
                  <div style="font-size:9px;color:#475569;letter-spacing:1px">RISK</div>
                  <div style="font-size:16px;font-weight:800;color:#ef4444;font-family:'JetBrains Mono'">{e['risk_score']}</div>
                </div>
                <div style="background:#1a2235;border-radius:6px;padding:6px 10px;min-width:100px">
                  <div style="font-size:9px;color:#475569;letter-spacing:1px">IMMOBILITY</div>
                  <div style="font-size:16px;font-weight:800;color:#3b82f6;font-family:'JetBrains Mono'">{e['immobility_score']}</div>
                </div>
                <div style="background:#1a2235;border-radius:6px;padding:6px 10px;min-width:100px">
                  <div style="font-size:9px;color:#475569;letter-spacing:1px">URGENCY</div>
                  <div style="font-size:16px;font-weight:800;color:#f97316;font-family:'JetBrains Mono'">{e['urgency_score']}</div>
                </div>
                <div style="background:#1a2235;border-radius:6px;padding:6px 10px;min-width:100px">
                  <div style="font-size:9px;color:#475569;letter-spacing:1px">NEARBY HELP −</div>
                  <div style="font-size:16px;font-weight:800;color:#22c55e;font-family:'JetBrains Mono'">{e['nearby_help']}</div>
                </div>
                <div style="background:#1a2235;border-radius:6px;padding:6px 10px;min-width:100px">
                  <div style="font-size:9px;color:#475569;letter-spacing:1px">TEMP °C</div>
                  <div style="font-size:16px;font-weight:800;color:#fbbf24;font-family:'JetBrains Mono'">{e['temperature']}</div>
                </div>
                <div style="background:#1a2235;border-radius:6px;padding:6px 10px;min-width:100px">
                  <div style="font-size:9px;color:#475569;letter-spacing:1px">SMOKE</div>
                  <div style="font-size:16px;font-weight:800;color:#94a3b8;font-family:'JetBrains Mono'">{e['smoke_level']}</div>
                </div>
              </div>
              <div style="font-size:11px;color:#64748b;margin-top:8px">
                Fire distance: {e['min_fire_dist']} cells &nbsp;|&nbsp; {pfw}
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="slabel" style="margin-top:14px">Assignment Cost Formula</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="formula">
          <span class="eq">A</span> &nbsp;=&nbsp;
          <span class="var">α</span>·<span class="eq">Distance</span> &nbsp;+&nbsp;
          <span class="var">β</span>·<span class="eq">PathRisk</span> &nbsp;+&nbsp;
          <span class="var">γ</span>·<span class="eq">Load</span> &nbsp;−&nbsp;
          <span class="var">δ</span>·<span class="eq">SkillMatch</span>
          <br><br>
          <span style="color:#64748b;font-size:11px">
            α=1.0 (distance) &nbsp;|&nbsp; β=0.7 (path risk) &nbsp;|&nbsp;
            γ=0.4 (staff load) &nbsp;|&nbsp; δ=1.3 (skill match bonus)
          </span>
        </div>
        """, unsafe_allow_html=True)

        for a in asns.get("assignments", []):
            bd = a.get("cost_breakdown", {})
            st.markdown(f"""
            <div style="background:#0f1629;border:1px solid #1e2a40;border-left:4px solid #a855f7;
                        border-radius:9px;padding:10px 14px;margin-bottom:6px;
                        display:flex;justify-content:space-between;align-items:center">
              <div>
                <span style="font-weight:700;color:#a855f7;font-family:'JetBrains Mono'">
                  Staff {a['staff_id']}</span>
                <span style="color:#374151;margin:0 6px">→</span>
                <span style="font-weight:700;color:#3b82f6;font-family:'JetBrains Mono'">
                  Patient {a['patient_id']}</span>
                <div style="font-size:10px;color:#475569;margin-top:4px">
                  {a.get('route_note','')}
                </div>
              </div>
              <div style="font-size:11px;color:#64748b;font-family:'JetBrains Mono';text-align:right">
                dist={bd.get('distance','?')} | risk={bd.get('path_risk','?')}<br>
                skill_bonus={bd.get('skill_bonus','0')}<br>
                <b style="color:#e2e8f0">cost={bd.get('total_cost','?')}</b>
              </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#334155;padding:20px;text-align:center">Run a tick to see decision engine output.</div>', unsafe_allow_html=True)


# ══════════════ TAB 3 — AI PLANNER ════════════════════════════════════════════
with tab3:
    st.markdown('<div class="slabel">Simulation-Based Decision Making (Key Innovation)</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#0a1020;border:1px solid #1e2a40;border-radius:10px;
                padding:14px 18px;font-size:13px;color:#64748b;margin-bottom:16px;line-height:1.7">
      Before executing any response, the AI simulates <b style="color:#94a3b8">3 different plans</b>
      3 ticks into the future and selects the plan with the
      <b style="color:#22c55e">highest survival probability</b>.
      This is not a static decision — it runs every tick as conditions change.
    </div>
    """, unsafe_allow_html=True)

    plan_result = st.session_state.plan
    if plan_result and plan_result.get("plans"):
        plans = plan_result["plans"]
        cols  = st.columns(3)
        for i, p in enumerate(plans):
            is_rec = p.get("recommended", False)
            with cols[i]:
                brd   = "#22c55e" if is_rec else "#1e2a40"
                bg    = "linear-gradient(135deg,#082018,#051510)" if is_rec else "#0f1629"
                rbdg  = '<span class="rec-badge">✅ RECOMMENDED</span>' if is_rec else ""
                sc_c  = "#22c55e" if is_rec else "#94a3b8"
                st.markdown(f"""
                <div style="background:{bg};border:2px solid {brd};border-radius:12px;
                            padding:16px;height:100%;min-height:220px">
                  <div style="font-size:22px">{p['icon']}</div>
                  <div style="font-size:14px;font-weight:800;color:#f1f5f9;margin-top:6px">
                    {p['name']}{rbdg}
                  </div>
                  <div style="font-size:11px;color:#64748b;margin-top:5px">{p['description']}</div>
                  <div style="margin-top:12px">
                    <div style="font-size:9px;color:#475569;letter-spacing:1px">SURVIVAL PROBABILITY</div>
                    <div style="font-size:36px;font-weight:900;color:{sc_c};
                                font-family:'JetBrains Mono'">{p['survival_probability']}%</div>
                  </div>
                  <div style="display:flex;gap:12px;margin-top:8px">
                    <div>
                      <div style="font-size:9px;color:#475569">AT RISK</div>
                      <div style="font-weight:700;color:#f97316">{p['patients_at_risk']}</div>
                    </div>
                    <div>
                      <div style="font-size:9px;color:#475569">FIRE CELLS</div>
                      <div style="font-weight:700;color:#ef4444">{p['fire_cells_predicted']}</div>
                    </div>
                    <div>
                      <div style="font-size:9px;color:#475569">RISK SCORE</div>
                      <div style="font-weight:700;color:#94a3b8">{p['total_risk_score']}</div>
                    </div>
                  </div>
                  <div style="font-size:10px;color:#475569;margin-top:8px;font-style:italic">
                    {p['tradeoff']}
                  </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="reasoning">
          🤖 <b>AI Reasoning:</b> {plan_result['reasoning']}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#334155;padding:30px;text-align:center">Run a tick to activate the Simulation Planner.</div>', unsafe_allow_html=True)


# ══════════════ TAB 4 — VERIFICATION ══════════════════════════════════════════
with tab4:
    st.markdown('<div class="slabel">Verification Layer — Task Tracking</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#0a1020;border:1px solid #1e2a40;border-radius:10px;
                padding:13px 18px;font-size:13px;color:#64748b;margin-bottom:14px;line-height:1.7">
      The Verification Layer ensures tasks are <b style="color:#94a3b8">actually completed</b> —
      not just assigned. It uses staff location + fire/smoke data to
      <b style="color:#94a3b8">probabilistically verify</b> completion.
      Failed tasks are automatically flagged for reassignment.
    </div>
    """, unsafe_allow_html=True)

    verif_state = st.session_state.verification
    verifier    = st.session_state.verifier

    if verifier and verifier.tasks:
        vcounts = verifier.summary()
        mc1, mc2, mc3, mc4 = st.columns(4)
        for col, label, val, color in [
            (mc1, "Active",   vcounts.get("active",0),    "#3b82f6"),
            (mc2, "Complete", vcounts.get("completed",0) + vcounts.get("likely_complete",0), "#22c55e"),
            (mc3, "Failed",   vcounts.get("failed",0),    "#ef4444"),
            (mc4, "Total",    vcounts.get("total",0),     "#94a3b8"),
        ]:
            col.markdown(f"""
            <div style="background:#0f1629;border:1px solid #1e2a40;border-radius:9px;
                        padding:12px;text-align:center">
              <div style="font-size:9px;color:#475569;letter-spacing:1px">{label.upper()}</div>
              <div style="font-size:28px;font-weight:900;color:{color};
                          font-family:'JetBrains Mono'">{val}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="slabel" style="margin-top:14px">Task Registry</div>', unsafe_allow_html=True)

        status_color = {
            "active":         ("#3b82f6", "vstatus-active"),
            "likely_complete":("#84cc16",  "vstatus-likely"),
            "completed":      ("#22c55e",  "vstatus-complete"),
            "failed":         ("#ef4444",  "vstatus-failed"),
        }
        for tid, task in verifier.tasks.items():
            s    = task["status"]
            sc, sclass = status_color.get(s, ("#94a3b8", "vstatus-active"))
            conf = task.get("confidence", 1.0)
            cpct = int(conf*100)
            icon = {"active":"⏳","likely_complete":"🔄","completed":"✅","failed":"❌"}.get(s,"❓")
            fail_note = f'<div style="font-size:10px;color:#ef4444;margin-top:3px">{task.get("fail_reason","")}</div>' if task.get("fail_reason") else ""
            st.markdown(f"""
            <div class="vtask">
              <div>
                <span style="font-family:'JetBrains Mono';font-weight:700;color:#94a3b8">{tid}</span>
                &nbsp;
                <span style="color:#a855f7;font-weight:700">Staff {task['staff_id']}</span>
                <span style="color:#374151;margin:0 5px">→</span>
                <span style="color:#3b82f6;font-weight:700">Patient {task['patient_id']}</span>
                <div style="font-size:10px;color:#475569;margin-top:2px">
                  Assigned tick {task['assigned_tick']} | Deadline tick {task['deadline_tick']}
                  &nbsp;|&nbsp; Room {task['target_room']}
                </div>
                {fail_note}
              </div>
              <div style="text-align:right">
                <div class="{sclass}">{icon} {s.replace('_',' ').upper()}</div>
                <div style="font-size:9px;color:#475569;margin-top:3px">Confidence</div>
                <div class="conf-bar">
                  <div class="conf-fill" style="width:{cpct}%;background:{sc}"></div>
                </div>
                <div style="font-size:9px;color:{sc};font-family:'JetBrains Mono';margin-top:2px">{cpct}%</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        if verif_state.get("reassign_needed"):
            st.markdown('<div class="slabel" style="margin-top:14px;color:#ef4444">⚠️ Reassignment Triggered</div>', unsafe_allow_html=True)
            for r in verif_state["reassign_needed"]:
                st.markdown(f"""
                <div style="background:#1a0a0a;border:1px solid #ef444450;border-radius:8px;
                            padding:10px 14px;margin-bottom:6px">
                  <span style="color:#ef4444;font-weight:700">Patient {r['patient_id']}</span>
                  <span style="color:#475569;font-size:12px;margin-left:8px">{r['reason']}</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#334155;padding:30px;text-align:center">Run ticks to populate the verification layer.</div>', unsafe_allow_html=True)


# ══════════════ TAB 5 — FIREFIGHTER MODE ═════════════════════════════════════
with tab5:
    if not st.session_state.ff_joined:
        st.markdown("""
        <div style="text-align:center;padding:50px 20px">
          <div style="font-size:48px">🚒</div>
          <div style="font-size:16px;font-weight:700;color:#475569;margin-top:12px">
            Firefighters Not Yet On Scene
          </div>
          <div style="font-size:13px;color:#334155;margin-top:6px">
            Press <b>🚒 Firefighters Arrive</b> in the sidebar to activate this panel.
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        ff = st.session_state.ff_briefing
        if ff:
            st.markdown(f"""
            <div class="ff-brief">
              <div class="ff-title">🚒 FIREFIGHTER BRIEFING — Tick {ff['tick']}</div>
              <div class="ff-line">
                Active fire cells: <b style="color:#ef4444">{ff['fire_cell_count']}</b>
                &nbsp;|&nbsp; Spread direction: <b style="color:#f97316">{ff['fire_spread_direction']}</b>
                &nbsp;|&nbsp; Internal staff: <b style="color:#a855f7">{ff['internal_staff_count']}</b>
                &nbsp;|&nbsp; Critical patients needing FF: <b style="color:#3b82f6">{len(ff['critical_patients'])}</b>
              </div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)

            with c1:
                st.markdown('<div class="slabel">✅ Safe Entry Points</div>', unsafe_allow_html=True)
                for i, ep in enumerate(ff["safe_entry_points"][:3]):
                    is_rec = (ep == ff["recommended_entry"])
                    rec    = " — ⭐ RECOMMENDED" if is_rec else ""
                    bc     = "#22c55e" if is_rec else "#1e2a40"
                    st.markdown(f"""
                    <div class="ff-entry" style="border-color:{bc}50">
                      <span style="font-weight:700;color:#22c55e;font-family:'JetBrains Mono'">
                        Entry {i+1}: ({ep[0]}, {ep[1]})</span>
                      <span style="font-size:11px;color:#4ade80">{rec}</span>
                      <div style="font-size:10px;color:#475569;margin-top:3px">
                        No fire · Smoke level below threshold · Accessible
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown('<div class="slabel" style="margin-top:12px">🔴 High Priority Fire Zones</div>', unsafe_allow_html=True)
                for z in ff["hot_zones"][:4]:
                    st.markdown(f"""
                    <div class="ff-zone">
                      <span style="font-weight:700;color:#ef4444;font-family:'JetBrains Mono'">
                        Cell ({z['cell'][0]}, {z['cell'][1]})</span>
                      <span style="background:#3b0a0a;color:#ef4444;font-size:9px;
                                   padding:2px 7px;border-radius:10px;margin-left:6px">
                        {z['label']}</span>
                      <div style="font-size:10px;color:#475569;margin-top:3px">
                        Contains active high-severity fire — approach from upwind
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

            with c2:
                st.markdown('<div class="slabel">🏥 Critical Patients Needing FF Help</div>', unsafe_allow_html=True)
                if ff["critical_patients"]:
                    for cp in ff["critical_patients"]:
                        urg_c = "#ef4444" if cp["urgency"] == "IMMEDIATE" else "#f97316"
                        st.markdown(f"""
                        <div class="ff-patient">
                          <div style="display:flex;justify-content:space-between">
                            <span style="font-weight:700;color:#3b82f6">Patient {cp['patient_id']}
                              <span style="color:#94a3b8;font-size:11px;margin-left:6px">{cp['type']}</span>
                            </span>
                            <span style="background:#1a0a0a;color:{urg_c};font-size:9px;
                                         font-weight:800;padding:2px 8px;border-radius:10px">
                              {cp['urgency']}
                            </span>
                          </div>
                          <div style="font-size:11px;color:#475569;margin-top:4px;font-family:'JetBrains Mono'">
                            Location: ({cp['location'][0]}, {cp['location'][1]})
                            &nbsp;|&nbsp; Fire dist: {cp['fire_distance']} cells
                            &nbsp;|&nbsp; Smoke: {cp['smoke_level']}
                          </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown('<div style="color:#334155;font-size:13px;padding:10px">No critical patients requiring FF at this tick.</div>', unsafe_allow_html=True)

                st.markdown('<div class="slabel" style="margin-top:12px">📡 Predicted Fire Spread (3 Ticks)</div>', unsafe_allow_html=True)
                pred_cells = ff.get("predicted_fire_cells", [])
                if pred_cells:
                    cell_str = ", ".join(f"({x},{y})" for x,y in pred_cells[:8])
                    more = f" ... +{len(pred_cells)-8} more" if len(pred_cells) > 8 else ""
                    st.markdown(f"""
                    <div style="background:#1a1500;border:1px solid #eab30840;border-radius:8px;
                                padding:12px 14px">
                      <div style="font-size:9px;color:#eab308;font-weight:700;
                                  letter-spacing:1px;margin-bottom:6px">PREDICTED CELLS (3 TICKS)</div>
                      <div style="font-family:'JetBrains Mono';font-size:11px;color:#92400e">
                        {cell_str}{more}
                      </div>
                      <div style="font-size:10px;color:#475569;margin-top:6px">
                        Avoid these zones — fire expected to reach within 3 ticks
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:#0a1020;border:1px solid #1e2a40;border-radius:10px;
                        padding:14px 18px;margin-top:16px">
              <div style="font-size:11px;font-weight:700;color:#475569;letter-spacing:1px;
                           margin-bottom:6px">⚡ COORDINATED ACTION PLAN</div>
              <div style="font-size:13px;color:#64748b;line-height:1.8">
                Internal staff handling patients at coordinates:
                <b style="color:#a855f7">{", ".join(f"({a['target_room']})" for a in asns.get("assignments",[]))}</b><br>
                Firefighters should focus on zones not covered by internal staff.<br>
                All responders operating on the same live building map — no time wasted on orientation.
              </div>
            </div>
            """, unsafe_allow_html=True)
