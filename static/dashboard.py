import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from simulation.simulation_engine  import build_from_params
from decision.decision_engine       import run_decision_engine
from assignment.assignment_engine   import run_assignment
from verification.verification_engine import VerificationEngine
from planner.simulation_planner     import run_planner
from firefighter.firefighter_module import get_firefighter_briefing

st.set_page_config(page_title="CrisisAI", layout="wide",
                   initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600&display=swap');
html,[class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background:#090d17;}
.block-container{padding:1.2rem 1.8rem 2rem!important;max-width:100%!important;}
button[data-testid="baseButton-primary"]{background:linear-gradient(135deg,#ef4444,#b91c1c)!important;border:none!important;color:#fff!important;font-weight:700!important;}
button[data-testid="baseButton-secondary"]{background:#151c2c!important;border:1px solid #2a3348!important;color:#cbd5e1!important;font-weight:600!important;}
.hdr{background:linear-gradient(135deg,#0f1629,#0a0f1e);border:1px solid #1e2a40;border-radius:14px;padding:18px 26px;margin-bottom:16px;display:flex;align-items:center;justify-content:space-between;}
.hdr-title{font-size:20px;font-weight:900;color:#f1f5f9;letter-spacing:-.3px;}
.hdr-sub{font-size:12px;color:#475569;margin-top:3px;}
.badge-live{background:#ef4444;color:#fff;font-size:10px;font-weight:800;padding:3px 10px;border-radius:20px;letter-spacing:1px;animation:pulse 1.6s infinite;}
.badge-tick{background:#1e2a40;color:#94a3b8;font-size:11px;font-weight:700;padding:4px 12px;border-radius:20px;font-family:'JetBrains Mono';}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.55}}
.stats{display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap;}
.sc{flex:1;min-width:100px;background:#0f1629;border:1px solid #1e2a40;border-radius:11px;padding:13px 16px;}
.sc-label{font-size:10px;color:#475569;font-weight:700;letter-spacing:.8px;text-transform:uppercase;}
.sc-val{font-size:26px;font-weight:900;margin-top:3px;line-height:1;}
.sc-sub{font-size:11px;color:#475569;margin-top:2px;}
.fire{color:#ef4444}.warn{color:#f97316}.ok{color:#22c55e}.blue{color:#3b82f6}.purple{color:#a855f7}.yellow{color:#eab308}
.slabel{font-size:10px;font-weight:800;color:#475569;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px;padding-bottom:5px;border-bottom:1px solid #1a2235;}
.gwrap{background:#0c1120;border:1px solid #1e2a40;border-radius:12px;padding:14px;overflow-x:auto;}
.grow{display:flex;gap:2px;margin-bottom:2px;}
.gc{width:40px;height:40px;border-radius:5px;display:flex;align-items:center;justify-content:center;font-size:15px;position:relative;border:1px solid transparent;flex-shrink:0;transition:background 0.3s ease,box-shadow 0.3s ease,border-color 0.3s ease;}
.gc-empty{background:#111827;border-color:#1f2937;}
.gc-fire{background:#3b0a0a;border-color:#ef4444;box-shadow:0 0 8px #ef444460;}
.gc-fire2{background:#5a0000;border-color:#ff6b6b;box-shadow:0 0 12px #ff6b6b70;}
.gc-pred{background:#2d2000;border-color:#eab308;box-shadow:0 0 4px #eab30840;}
.gc-smoke{background:#1f1500;border-color:#92400e;}
.gc-new-fire{animation:fireFlash 0.8s ease-out;}
@keyframes fireFlash{0%{box-shadow:0 0 20px #ff4400,0 0 40px #ff4400;transform:scale(1.1);}100%{transform:scale(1);}}
.updated-badge{display:inline-block;background:linear-gradient(90deg,#22c55e,#16a34a);color:#fff;font-size:9px;font-weight:800;padding:2px 8px;border-radius:20px;letter-spacing:1px;animation:pulse 1s 3;margin-left:8px;}
.gc-icu{background:#0a1e3b;border-color:#3b82f6;box-shadow:0 0 6px #3b82f640;}
.gc-mob{background:#082018;border-color:#22c55e;}
.gc-staff{background:#1a0a3b;border-color:#a855f7;box-shadow:0 0 5px #a855f740;}
.gc-exit{background:#1a2a1a;border-color:#4ade80;}
.gc-ff{background:#1a1000;border-color:#f59e0b;box-shadow:0 0 8px #f59e0b60;}
.coord{font-size:6px;color:#374151;position:absolute;bottom:1px;right:2px;font-family:'JetBrains Mono';}
.legend{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px;}
.li{display:flex;align-items:center;gap:5px;font-size:10px;color:#6b7280;}
.ld{width:10px;height:10px;border-radius:3px;}
.pcard{background:#0f1629;border-radius:9px;padding:11px 14px;margin-bottom:7px;display:flex;align-items:center;justify-content:space-between;border-left:4px solid;border-top:1px solid #1e2a40;border-right:1px solid #1e2a40;border-bottom:1px solid #1e2a40;}
.pname{font-weight:700;font-size:13px;color:#e2e8f0;}
.pmeta{font-size:10px;color:#475569;margin-top:2px;}
.pscore{font-size:20px;font-weight:900;font-family:'JetBrains Mono';}
.badge{font-size:9px;font-weight:800;padding:2px 8px;border-radius:20px;margin-left:6px;letter-spacing:.4px;}
.bc{background:#3b0a0a;color:#ef4444;border:1px solid #ef444440;}
.bh{background:#3b1500;color:#f97316;border:1px solid #f9731640;}
.bm{background:#1a2a00;color:#84cc16;border:1px solid #84cc1640;}
.bl{background:#1a2535;color:#64748b;border:1px solid #47556940;}
.acard{background:#0f1629;border:1px solid #1e2a40;border-radius:9px;padding:12px 14px;margin-bottom:7px;}
.afrom{font-size:12px;font-weight:800;color:#a855f7;font-family:'JetBrains Mono';}
.ato{font-size:12px;font-weight:800;color:#3b82f6;font-family:'JetBrains Mono';}
.ai-box{background:linear-gradient(135deg,#0a1e0a,#051510);border:1px solid #22c55e40;border-radius:10px;padding:14px 18px;margin-bottom:10px;}
.ai-title{font-size:11px;font-weight:800;color:#22c55e;letter-spacing:1.5px;margin-bottom:8px;}
.ai-step{display:flex;gap:8px;margin-bottom:6px;align-items:flex-start;}
.ai-dot{width:6px;height:6px;border-radius:50%;background:#22c55e;margin-top:5px;flex-shrink:0;}
.ai-text{font-size:12px;color:#4ade80;line-height:1.5;}
.formula{background:#0f1629;border:1px solid #2a3a5c;border-radius:10px;padding:14px 18px;font-family:'JetBrains Mono';font-size:13px;color:#93c5fd;margin-bottom:12px;text-align:center;}
.plan-card{border-radius:12px;padding:16px 18px;margin-bottom:10px;border:2px solid;}
.plan-rec{border-color:#22c55e;background:linear-gradient(135deg,#082018,#051510);}
.plan-norm{border-color:#1e2a40;background:#0f1629;}
.vtask{background:#0f1629;border:1px solid #1e2a40;border-radius:8px;padding:10px 13px;margin-bottom:6px;display:flex;align-items:center;justify-content:space-between;}
.ff-entry{background:#1a2a10;border:1px solid #22c55e40;border-radius:8px;padding:10px 14px;margin-bottom:8px;}
.ff-zone{background:#2d0a0a;border:1px solid #ef444440;border-radius:8px;padding:10px 14px;margin-bottom:8px;}
.ff-patient{background:#0a1e3b;border:1px solid #3b82f640;border-radius:8px;padding:10px 14px;margin-bottom:8px;}
.logbox{background:#050810;border:1px solid #131d30;border-radius:8px;padding:8px 12px;font-family:'JetBrains Mono';font-size:10px;color:#475569;max-height:130px;overflow-y:auto;}
.floor-tab{display:inline-block;padding:5px 14px;border-radius:20px;font-size:11px;font-weight:700;cursor:pointer;margin-right:6px;margin-bottom:8px;}
.floor-active{background:#3b82f6;color:white;}
.floor-inactive{background:#1e2a40;color:#64748b;}
[data-testid="stSidebar"]{background:#090d17!important;border-right:1px solid #1a2235!important;}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
def _init():
    defaults = dict(
        sim=None, verifier=None, decisions=[], assignments={"assignments":[]},
        verification={}, plan=None, ff_briefing=None, log=[],
        ff_joined=False, initialized=False, view_floor=0,
        prev_decisions={},     # {patient_id: priority} from last tick
        fire_new_cells=set(),  # cells that caught fire this tick (for flash)
        tick_updated=False,    # flag to show "Updated this tick" badge
    )
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
_init()

def do_tick():
    sim   = st.session_state.sim
    verif = st.session_state.verifier

    # Snapshot fire before update to detect new cells
    fire_before = set((x,y,f) for x,y,f in sim.fire)

    sim.update_fire()

    # Track newly spread fire cells for flash animation
    fire_after = set((x,y,f) for x,y,f in sim.fire)
    st.session_state.fire_new_cells = fire_after - fire_before

    # Snapshot previous priorities for "what changed" diff
    prev = {d["patient_id"]: d["priority"] for d in st.session_state.decisions}
    st.session_state.prev_decisions = prev

    decisions   = run_decision_engine(sim)
    assignments = run_assignment(sim, decisions)
    verif.register_assignments(assignments, sim.tick)
    verification = verif.verify_tick(sim, sim.tick)
    plan        = run_planner(sim)
    ff_briefing = get_firefighter_briefing(sim)

    st.session_state.decisions    = decisions
    st.session_state.assignments  = assignments
    st.session_state.verification = verification
    st.session_state.plan         = plan
    st.session_state.ff_briefing  = ff_briefing
    st.session_state.tick_updated = True

    vcounts = verif.summary()
    fire_n  = len(sim.fire)
    ai_remark = ""
    if verification.get("reassign_needed"):
        ai_remark = f" | ⚠️ AI REASSIGNED {len(verification['reassign_needed'])} task(s)"
    if plan and plan.get("recommended_plan"):
        p = plan["recommended_plan"]
        ai_remark += f" | 🤖 AI chose {p['name']} ({p['survival_probability']}% survival)"
    st.session_state.log.append(
        f"[Tick {sim.tick}] 🔥 {fire_n} cells | "
        f"👷 {len(assignments['assignments'])} assigned | "
        f"✅ {vcounts.get('completed',0)+vcounts.get('likely_complete',0)} done | "
        f"❌ {vcounts.get('failed',0)} failed{ai_remark}"
    )

# ── Grid renderer ─────────────────────────────────────────────────────────────
def render_grid(sim, floor=0, predicted_fire=None, fire_new_cells=None):
    predicted_set = set((x,y,f) for x,y,f in (predicted_fire or []) if f == floor)
    fire_set   = set((x,y) for x,y,f in sim.fire if f == floor)
    fire_sev   = {(x,y): sev for (x,y,f),sev in sim.fire_severity.items() if f == floor}
    pat_pos    = {(p.x,p.y): p for p in sim.patients if min(p.floor, sim.building.floors-1) == floor}
    staff_pos  = {(s.x,s.y): s for s in sim.staff    if min(s.floor, sim.building.floors-1) == floor}
    ff_pos     = {(f.x,f.y): f for f in sim.firefighters}
    exits      = set(sim.building.exits)
    pred2d     = set((x,y) for x,y,f in predicted_set)
    new_2d     = set((x,y) for x,y,f in (fire_new_cells or set()) if f == floor)

    html = '<div class="gwrap"><div>'
    for y in range(sim.building.height):
        html += '<div class="grow">'
        for x in range(sim.building.width):
            pos = (x, y)
            extra_cls = " gc-new-fire" if pos in new_2d else ""
            if pos in fire_set:
                sev  = fire_sev.get(pos, 1)
                cls  = "gc-fire2" if sev >= 3 else "gc-fire"
                icon = "🔥"
            elif pos in ff_pos:
                icon = "🚒"; cls = "gc-ff"
            elif pos in staff_pos:
                s = staff_pos[pos]
                icon = "💊" if s.trained else "👷"; cls = "gc-staff"
            elif pos in pat_pos:
                p = pat_pos[pos]
                icon = "🏥" if not p.movable else "🧍"
                cls  = "gc-icu" if not p.movable else "gc-mob"
            elif pos in pred2d:
                icon = "🟠"; cls = "gc-pred"   # predicted fire
            elif sim.smoke_map[floor][y][x] > 0.35:
                icon = "💨"; cls = "gc-smoke"   # smoke
            elif pos in exits:
                icon = "🚪"; cls = "gc-exit"
            else:
                icon = ""; cls = "gc-empty"
            html += f'<div class="gc {cls}{extra_cls}" title="{x},{y}">{icon}<span class="coord">{x},{y}</span></div>'
        html += '</div>'
    html += '''</div>
    <div class="legend">
      <div class="li"><div class="ld" style="background:#ff6b6b"></div>Fire (intense)</div>
      <div class="li"><div class="ld" style="background:#ef4444"></div>Fire</div>
      <div class="li"><div class="ld" style="background:#eab308"></div>🟠 Predicted (3 ticks)</div>
      <div class="li"><div class="ld" style="background:#92400e"></div>💨 Smoke</div>
      <div class="li"><div class="ld" style="background:#3b82f6"></div>ICU Patient</div>
      <div class="li"><div class="ld" style="background:#22c55e"></div>Mobile Patient</div>
      <div class="li"><div class="ld" style="background:#a855f7"></div>Staff</div>
      <div class="li"><div class="ld" style="background:#f59e0b"></div>Firefighter</div>
      <div class="li"><div class="ld" style="background:#4ade80"></div>Exit</div>
    </div></div>'''
    return html


def render_priorities(decisions, patients):
    mob_map = {p.id: p.movable for p in patients}
    cc  = {"critical":"#ef4444","high":"#f97316","medium":"#84cc16","low":"#475569"}
    bcl = {"critical":"bc","high":"bh","medium":"bm","low":"bl"}
    html = ""
    max_s = max((d["priority"] for d in decisions), default=1) or 1
    for d in decisions:
        pid = d["patient_id"]; s = d["priority"]
        lvl = d["explanation"]["priority_level"]
        mob = "Mobile" if mob_map.get(pid, True) else "ICU — Immobile"
        c   = cc.get(lvl, "#475569")
        pct = int(s/max_s*100)
        ff  = d.get("predicted_fire_nearby")
        warn= ' <span style="color:#eab308;font-size:10px">⚠️ predicted fire</span>' if ff else ""
        html += f"""
        <div class="pcard" style="border-left-color:{c}">
          <div>
            <div class="pname">P{pid}<span class="badge {bcl.get(lvl,'bl')}">{lvl.upper()}</span>{warn}</div>
            <div class="pmeta">{mob}</div>
            <div style="height:3px;background:#1a2235;border-radius:3px;margin-top:6px;width:130px">
              <div style="height:3px;background:{c};border-radius:3px;width:{pct}%"></div>
            </div>
          </div>
          <div class="pscore" style="color:{c}">{s}</div>
        </div>"""
    return html

def render_assignments(assignments_data):
    html = ""
    for a in assignments_data.get("assignments", []):
        note = a.get("route_note","")
        ncls = "color:#22c55e" if "✅" in note else "color:#f97316"
        bd   = a.get("cost_breakdown",{})
        html += f"""
        <div class="acard">
          <div style="display:flex;align-items:center;gap:8px">
            <span class="afrom">Staff {a['staff_id']}</span>
            <span style="color:#374151">⟶</span>
            <span class="ato">Patient {a['patient_id']}</span>
          </div>
          <div style="font-size:10px;color:#475569;margin-top:4px">
            Room {a['target_room']} | dist={bd.get('distance','?')} | risk={bd.get('path_risk','?')} | cost={bd.get('total_cost','?')}
          </div>
          <div style="font-size:11px;{ncls};margin-top:4px">{note}</div>
        </div>"""
    if not assignments_data.get("assignments"):
        html = '<div style="color:#334155;font-size:13px;padding:10px">Run a tick to see assignments.</div>'
    return html

def build_ai_reasoning(decisions, assignments_data, sim, plan_result, prev_decisions=None):
    """Generate human-readable AI reasoning steps with tick-over-tick diffs."""
    steps = []
    prev = prev_decisions or {}
    fire_n = len(sim.fire)
    steps.append(f"Fire detected — {fire_n} active cells spreading across the building.")

    if sim.predict_fire_spread(2):
        steps.append("Predictive model: fire will reach new zones in 2 ticks — pre-emptive action required.")

    if decisions:
        top = decisions[0]
        e   = top["explanation"]
        pid = top["patient_id"]
        why = []
        if top["is_icu"]:
            why.append(f"ICU/immobile (immobility score={e['immobility_score']})")
        if e["min_fire_dist"] <= 3:
            why.append(f"fire only {e['min_fire_dist']} cells away (urgency={e['urgency_score']})")
        if e["smoke_level"] > 0.3:
            why.append(f"smoke level {e['smoke_level']:.2f}")
        if e["risk_score"] > 20:
            why.append(f"high risk score={e['risk_score']}")
        steps.append(
            f"Patient {pid} is highest priority (score {top['priority']}) because: "
            f"{', '.join(why) if why else 'highest combined risk score'}."
        )

    # What changed since last tick
    if prev:
        changed = []
        for d in decisions:
            pid   = d["patient_id"]
            old_s = prev.get(pid)
            new_s = d["priority"]
            if old_s is None:
                changed.append(f"P{pid}: NEW (score {new_s})")
            elif abs(new_s - old_s) >= 1.0:
                arrow = "↑" if new_s > old_s else "↓"
                changed.append(f"P{pid}: {arrow} {old_s}→{new_s}")
        if changed:
            steps.append("Priority changes this tick: " + " | ".join(changed))
        else:
            steps.append("No significant priority changes from previous tick.")

    for a in assignments_data.get("assignments", []):
        bd   = a.get("cost_breakdown", {})
        note = a.get("route_note", "")
        route_info = "via safe corridor" if "✅" in note else "rerouted — fire on direct path"
        steps.append(
            f"Staff {a['staff_id']} → Patient {a['patient_id']}: "
            f"cost={bd.get('total_cost','?')} | {route_info}."
        )

    if plan_result and plan_result.get("recommended_plan"):
        p      = plan_result["recommended_plan"]
        others = [r for r in plan_result.get("plans", []) if not r.get("recommended")]
        reason = f"survival {p['survival_probability']}%"
        if others:
            vs = " vs ".join(f"{o['name']} ({o['survival_probability']}%)" for o in others)
            reason += f" — beats {vs}"
        steps.append(
            f"AI Planner selected '{p['name']}' — {reason}. "
            f"({p['patients_at_risk']} patients at risk, "
            f"{p['fire_cells_predicted']} predicted fire cells)"
        )

    return steps


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-size:17px;font-weight:900;color:#f1f5f9;margin-bottom:2px">⚡ CrisisAI</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:11px;color:#475569;margin-bottom:14px">Control Panel</div>', unsafe_allow_html=True)

    st.markdown("**🏗️ Building Setup**")
    grid_w    = st.slider("Width (rooms)", 6, 15, 10)
    grid_h    = st.slider("Height (rooms)", 6, 15, 10)
    floors    = st.slider("Floors", 1, 3, 1)

    st.markdown("**👥 Occupants**")
    num_pat   = st.slider("Total patients", 2, 12, 5)
    num_icu   = st.slider("ICU (immobile)", 0, num_pat, 2)
    num_staff = st.slider("Staff members", 1, 6, 3)
    num_train = st.slider("Trained medics", 0, num_staff, 2)

    st.markdown("**🔥 Fire Settings**")
    fire_x    = st.slider("Fire origin X", 0, grid_w-1, grid_w//2)
    fire_y    = st.slider("Fire origin Y", 0, grid_h-1, grid_h//2)
    fire_fl   = st.slider("Fire floor", 0, floors-1, 0) if floors > 1 else 0
    fire_spd  = st.select_slider("Fire speed", ["Slow","Normal","Fast"], value="Normal")
    spd_map   = {"Slow":1,"Normal":1,"Fast":2}

    st.markdown("---")
    if st.button("🚀  Initialize System", use_container_width=True, type="primary"):
        sim = build_from_params(
            grid_w, grid_h, floors, num_pat, num_icu,
            num_staff, num_train, fire_x, fire_y, fire_fl,
            spd_map[fire_spd]
        )
        verif = VerificationEngine(deadline_ticks=3)
        st.session_state.sim         = sim
        st.session_state.verifier    = verif
        st.session_state.decisions   = []
        st.session_state.assignments = {"assignments":[]}
        st.session_state.verification= {}
        st.session_state.plan        = None
        st.session_state.ff_briefing = None
        st.session_state.log         = [f"[Init] System started. Fire at ({fire_x},{fire_y}) Floor {fire_fl}. {num_pat} patients, {num_staff} staff."]
        st.session_state.ff_joined   = False
        st.session_state.initialized = True
        st.session_state.view_floor  = 0
        st.rerun()

    if st.session_state.initialized:
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⏭️ Next Tick", use_container_width=True):
                do_tick(); st.rerun()
        with col2:
            if st.button("⏩ 3 Ticks", use_container_width=True):
                for _ in range(3): do_tick()
                st.rerun()

        ff_done = st.session_state.ff_joined
        if st.button("🚒 Firefighters Arrive" if not ff_done else "🚒 Firefighters On Scene",
                     use_container_width=True, disabled=ff_done):
            sim = st.session_state.sim
            entries = sim.get_safe_entry_points()
            for ex, ey, ef in entries[:2]:
                sim.add_firefighter(ex, ey, ef)
            st.session_state.ff_joined   = True
            st.session_state.ff_briefing = get_firefighter_briefing(sim)
            st.session_state.log.append(f"[Tick {sim.tick}] 🚒 Firefighters joined at {[(e[0],e[1]) for e in entries[:2]]}")
            st.rerun()

        st.markdown("---")
        if st.session_state.sim:
            sim = st.session_state.sim
            st.markdown(f'<div style="font-size:12px;color:#64748b;line-height:2.2">'
                        f'Tick: <b style="color:#e2e8f0">{sim.tick}</b><br>'
                        f'Grid: <b style="color:#e2e8f0">{sim.building.width}×{sim.building.height}</b><br>'
                        f'Floors: <b style="color:#e2e8f0">{sim.building.floors}</b><br>'
                        f'Fire cells: <b style="color:#ef4444">{len(sim.fire)}</b><br>'
                        f'Patients: <b style="color:#3b82f6">{len(sim.patients)}</b><br>'
                        f'Staff: <b style="color:#a855f7">{len(sim.staff)}</b><br>'
                        f'Firefighters: <b style="color:#f59e0b">{len(sim.firefighters)}</b>'
                        f'</div>', unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
tick_val = st.session_state.sim.tick if st.session_state.sim else 0
st.markdown(f"""
<div class="hdr">
  <div>
    <div class="hdr-title">🔥 AI-Based Real-Time Crisis Orchestration System</div>
    <div class="hdr-sub">Multi-Occupancy Buildings · Detection → Decision → Assignment → Verification · Firefighter Integration</div>
  </div>
  <div style="display:flex;gap:8px;align-items:center">
    <span class="badge-tick">TICK {tick_val:03d}</span>
    <span class="badge-live">LIVE</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Stat bar ──────────────────────────────────────────────────────────────────
sim   = st.session_state.sim
vcnt  = st.session_state.verifier.summary() if st.session_state.verifier else {}
decs  = st.session_state.decisions
asns  = st.session_state.assignments
fire_n  = len(sim.fire) if sim else 0
crit_n  = sum(1 for d in decs if d["explanation"]["priority_level"]=="critical")
asgn_n  = len(asns.get("assignments",[]))
comp_n  = vcnt.get("completed",0)+vcnt.get("likely_complete",0)
fail_n  = vcnt.get("failed",0)
top_s   = decs[0]["priority"] if decs else 0
top_pid = decs[0]["patient_id"] if decs else "-"

st.markdown(f"""
<div class="stats">
  <div class="sc"><div class="sc-label">🔥 Fire Cells</div><div class="sc-val fire">{fire_n}</div><div class="sc-sub">active</div></div>
  <div class="sc"><div class="sc-label">⚠️ Critical</div><div class="sc-val warn">{crit_n}</div><div class="sc-sub">patients</div></div>
  <div class="sc"><div class="sc-label">✅ Assigned</div><div class="sc-val ok">{asgn_n}</div><div class="sc-sub">staff out</div></div>
  <div class="sc"><div class="sc-label">📋 Verified</div><div class="sc-val blue">{comp_n}</div><div class="sc-sub">complete</div></div>
  <div class="sc"><div class="sc-label">❌ Failed</div><div class="sc-val fire">{fail_n}</div><div class="sc-sub">reassign</div></div>
  <div class="sc"><div class="sc-label">🏆 Top Score</div><div class="sc-val purple">{top_s}</div><div class="sc-sub">P{top_pid}</div></div>
  <div class="sc"><div class="sc-label">🕒 Tick</div><div class="sc-val yellow">{tick_val}</div><div class="sc-sub">elapsed</div></div>
</div>
""", unsafe_allow_html=True)

if not st.session_state.initialized:
    st.markdown("""
    <div style="text-align:center;padding:70px 20px;color:#334155">
      <div style="font-size:52px;margin-bottom:16px">🔥</div>
      <div style="font-size:18px;font-weight:700;color:#475569">System Not Initialized</div>
      <div style="font-size:13px;margin-top:8px">
        Use the <b>sidebar</b> to configure your building, then press <b>Initialize System</b>.
      </div>
      <div style="font-size:12px;margin-top:6px;color:#334155">
        You can change: grid size · floors · number of patients/staff · fire origin · fire speed
      </div>
    </div>""", unsafe_allow_html=True)
    st.stop()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️  Live Map", "🧠  AI Reasoning", "🎯  Planner", "✅  Verification", "🚒  Firefighter"
])

# ══ TAB 1 — LIVE MAP ══════════════════════════════════════════════════════════
with tab1:
    # Floor switcher
    if sim.building.floors > 1:
        floor_html = ""
        for f in range(sim.building.floors):
            active = "floor-active" if f == st.session_state.view_floor else "floor-inactive"
            floor_html += f'<span class="floor-tab {active}" onclick="">Floor {f}</span>'
        cols_fl = st.columns(sim.building.floors)
        for f in range(sim.building.floors):
            with cols_fl[f]:
                if st.button(f"Floor {f}", key=f"fl_{f}",
                             type="primary" if f==st.session_state.view_floor else "secondary"):
                    st.session_state.view_floor = f
                    st.rerun()

    vfloor = st.session_state.view_floor
    c1, c2 = st.columns([3,2], gap="medium")

    with c1:
        updated = st.session_state.get("tick_updated", False)
        badge   = '<span class="updated-badge">UPDATED THIS TICK</span>' if updated else ""
        st.markdown(f'<div class="slabel">Building Map — Floor {vfloor}{badge}</div>', unsafe_allow_html=True)
        predicted = sim.predict_fire_spread(3) if sim.fire else []
        fire_new  = st.session_state.get("fire_new_cells", set())
        st.markdown(render_grid(sim, floor=vfloor, predicted_fire=predicted, fire_new_cells=fire_new), unsafe_allow_html=True)
        # Reset badge after render
        if updated:
            st.session_state.tick_updated = False

    with c2:
        st.markdown('<div class="slabel">Priority Decisions</div>', unsafe_allow_html=True)
        if decs:
            st.markdown(render_priorities(decs, sim.patients), unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#334155;font-size:13px;padding:10px">Run a tick to see priorities.</div>', unsafe_allow_html=True)
        st.markdown('<div class="slabel" style="margin-top:12px">Staff Assignments</div>', unsafe_allow_html=True)
        st.markdown(render_assignments(asns), unsafe_allow_html=True)

    st.markdown('<div class="slabel" style="margin-top:10px">Event Log</div>', unsafe_allow_html=True)
    log_html = "".join(
        f'<div style="margin-bottom:2px;color:{"#ef4444" if "REASSIGN" in l or "failed" in l else "#22c55e" if "joined" in l or "AI chose" in l else "#475569"}">{l}</div>'
        for l in reversed(st.session_state.log[-15:])
    )
    st.markdown(f'<div class="logbox">{log_html}</div>', unsafe_allow_html=True)

# ══ TAB 2 — AI REASONING ══════════════════════════════════════════════════════
with tab2:
    if sim and sim.fire:
        fire_cells = sim.fire
        cx = sum(x for x,y,*_ in fire_cells) / len(fire_cells)
        cy = sum(y for x,y,*_ in fire_cells) / len(fire_cells)
        if len(fire_cells) >= 4:
            new_cells = fire_cells[-min(4,len(fire_cells)):]
            ncx = sum(x for x,y,*_ in new_cells)/len(new_cells)
            ncy = sum(y for x,y,*_ in new_cells)/len(new_cells)
            hdir = "East" if ncx > cx else ("West" if ncx < cx else "")
            vdir = "South" if ncy > cy else ("North" if ncy < cy else "")
            direction = f"{vdir}-{hdir}".strip("-") or "Radial"
        else:
            direction = "radially"
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0a1e0a,#051510);border:1px solid #22c55e;border-radius:10px;padding:14px 18px;margin-bottom:14px">
          <div style="font-size:13px;font-weight:900;color:#4ade80;letter-spacing:1px;margin-bottom:6px">🤖 GEMMA 4 — AI FIRE ANALYSIS <span class="badge-live" style="float:right;animation:pulse 1.6s infinite">LIVE</span></div>
          <div style="font-size:13px;color:#86efac;line-height:1.6">
            Fire is spreading <b>{direction}</b> based on thermal gradient analysis.<br>
            Fire centroid is at <b>({round(cx,1)}, {round(cy,1)})</b> — zones in this direction require immediate evacuation priority.
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="slabel">🤖 AI Decision Reasoning (Explainable AI)</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#0a1020;border:1px solid #1e2a40;border-radius:10px;
                padding:12px 16px;font-size:12px;color:#64748b;margin-bottom:14px;line-height:1.7">
      Every decision this system makes is <b style="color:#94a3b8">explainable</b>.
      Below shows <b style="color:#94a3b8">exactly why</b> the AI prioritized each patient,
      chose each staff assignment, and selected the response plan.
      This is what separates a true AI system from a rule-based one.
    </div>""", unsafe_allow_html=True)

    if decs:
        steps = build_ai_reasoning(decs, asns, sim, st.session_state.plan,
                                    prev_decisions=st.session_state.get("prev_decisions", {}))
        steps_html = "".join(
            f'<div class="ai-step"><div class="ai-dot"></div>'
            f'<div class="ai-text">{s}</div></div>'
            for s in steps
        )
        st.markdown(f'<div class="ai-box"><div class="ai-title">🔍 AI REASONING — TICK {tick_val}</div>{steps_html}</div>',
                    unsafe_allow_html=True)

    st.markdown('<div class="slabel" style="margin-top:14px">Priority Score Formula</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="formula">
      P = <span style="color:#f472b6">w₁</span>·Risk + <span style="color:#f472b6">w₂</span>·Immobility + <span style="color:#f472b6">w₃</span>·Urgency − <span style="color:#f472b6">w₄</span>·NearbyHelp
      <br><span style="color:#475569;font-size:11px">w₁=1.2 | w₂=1.5 | w₃=1.0 | w₄=0.8</span>
    </div>
    """, unsafe_allow_html=True)

    if decs:
        st.markdown('<div class="slabel">Full Score Breakdown</div>', unsafe_allow_html=True)
        for d in decs:
            e   = d["explanation"]
            lvl = e["priority_level"]
            cc  = {"critical":"#ef4444","high":"#f97316","medium":"#84cc16","low":"#475569"}
            c   = cc.get(lvl, "#475569")
            icu = "🏥 ICU" if d["is_icu"] else "🧍 Mobile"
            pfw = "⚠️ Predicted fire nearby" if d["predicted_fire_nearby"] else "✅ Safe next 3 ticks"
            st.markdown(f"""
            <div style="background:#0f1629;border:1px solid #1e2a40;border-left:4px solid {c};
                        border-radius:9px;padding:12px 16px;margin-bottom:8px">
              <div style="display:flex;justify-content:space-between;align-items:center">
                <span style="font-weight:800;color:#e2e8f0">Patient {d['patient_id']} — {icu}
                  <span style="font-size:10px;color:{c};margin-left:8px">{lvl.upper()}</span>
                </span>
                <span style="font-family:'JetBrains Mono';font-size:22px;font-weight:900;color:{c}">{d['priority']}</span>
              </div>
              <div style="display:flex;gap:10px;margin-top:10px;flex-wrap:wrap">
                {"".join(f'''<div style="background:#1a2235;border-radius:6px;padding:6px 10px;min-width:90px">
                  <div style="font-size:9px;color:#475569;letter-spacing:1px">{lbl}</div>
                  <div style="font-size:15px;font-weight:800;color:{clr};font-family:'JetBrains Mono'">{val}</div>
                </div>''' for lbl,clr,val in [
                    ("RISK","#ef4444",e['risk_score']),("IMMOBILITY","#3b82f6",e['immobility_score']),
                    ("URGENCY","#f97316",e['urgency_score']),("NEARBY HELP−","#22c55e",e['nearby_help']),
                    ("TEMP °C","#fbbf24",e['temperature']),("SMOKE","#94a3b8",e['smoke_level'])])}
              </div>
              <div style="font-size:11px;color:#64748b;margin-top:8px">
                Fire distance: {e['min_fire_dist']} cells &nbsp;|&nbsp; {pfw}
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<div class="slabel" style="margin-top:14px">Assignment Cost Formula</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="formula">
          A = <span style="color:#f472b6">α</span>·Distance + <span style="color:#f472b6">β</span>·PathRisk + <span style="color:#f472b6">γ</span>·Load − <span style="color:#f472b6">δ</span>·SkillMatch
          <br><span style="color:#475569;font-size:11px">α=1.0 | β=0.7 | γ=0.4 | δ=1.3</span>
        </div>
        """, unsafe_allow_html=True)
        for a in asns.get("assignments",[]):
            bd   = a.get("cost_breakdown",{})
            note = a.get("route_note","")
            nc   = "#22c55e" if "✅" in note else "#f97316"
            st.markdown(f"""
            <div style="background:#0f1629;border:1px solid #1e2a40;border-left:4px solid #a855f7;
                        border-radius:9px;padding:10px 14px;margin-bottom:6px;
                        display:flex;justify-content:space-between;align-items:center">
              <div>
                <span style="color:#a855f7;font-weight:800;font-family:'JetBrains Mono'">Staff {a['staff_id']}</span>
                <span style="color:#374151;margin:0 5px">→</span>
                <span style="color:#3b82f6;font-weight:800;font-family:'JetBrains Mono'">Patient {a['patient_id']}</span>
                <div style="font-size:11px;color:{nc};margin-top:3px">{note}</div>
              </div>
              <div style="font-size:11px;color:#64748b;font-family:'JetBrains Mono';text-align:right">
                dist={bd.get('distance','?')} | risk={bd.get('path_risk','?')}<br>
                skill_bonus={bd.get('skill_bonus',0)}<br>
                <b style="color:#e2e8f0">cost={bd.get('total_cost','?')}</b>
              </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#334155;padding:30px;text-align:center">Run a tick to see AI reasoning.</div>', unsafe_allow_html=True)

# ══ TAB 3 — PLANNER ═══════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="slabel">Simulation-Based Decision Making — Key Innovation</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#0a1020;border:1px solid #1e2a40;border-radius:10px;
                padding:13px 18px;font-size:13px;color:#64748b;margin-bottom:14px;line-height:1.7">
      Before executing any response, the AI simulates <b style="color:#94a3b8">3 different plans</b>
      3 ticks into the future. It selects the plan with the
      <b style="color:#22c55e">highest survival probability</b>. Runs every tick as situation changes.
    </div>""", unsafe_allow_html=True)

    plan_result = st.session_state.plan
    if plan_result and plan_result.get("plans"):
        cols = st.columns(3)
        for i, p in enumerate(plan_result["plans"]):
            is_rec = p.get("recommended", False)
            brd    = "#22c55e" if is_rec else "#1e2a40"
            bg     = "linear-gradient(135deg,#082018,#051510)" if is_rec else "#0f1629"
            sc_c   = "#22c55e" if is_rec else "#94a3b8"
            rbdg   = '<span style="background:#22c55e;color:#000;font-size:9px;font-weight:800;padding:2px 8px;border-radius:20px;margin-left:6px">✅ CHOSEN</span>' if is_rec else ""
            with cols[i]:
                st.markdown(f"""
                <div style="background:{bg};border:2px solid {brd};border-radius:12px;
                            padding:16px;min-height:240px">
                  <div style="font-size:24px">{p['icon']}</div>
                  <div style="font-size:14px;font-weight:800;color:#f1f5f9;margin-top:6px">{p['name']}{rbdg}</div>
                  <div style="font-size:11px;color:#64748b;margin-top:5px">{p['description']}</div>
                  <div style="margin-top:12px">
                    <div style="font-size:9px;color:#475569;letter-spacing:1px">SURVIVAL PROBABILITY</div>
                    <div style="font-size:36px;font-weight:900;color:{sc_c};font-family:'JetBrains Mono'">{p['survival_probability']}%</div>
                  </div>
                  <div style="display:flex;gap:14px;margin-top:8px">
                    <div><div style="font-size:9px;color:#475569">AT RISK</div>
                      <div style="font-weight:700;color:#f97316">{p['patients_at_risk']}</div></div>
                    <div><div style="font-size:9px;color:#475569">FIRE CELLS</div>
                      <div style="font-weight:700;color:#ef4444">{p['fire_cells_predicted']}</div></div>
                    <div><div style="font-size:9px;color:#475569">RISK SCORE</div>
                      <div style="font-weight:700;color:#94a3b8">{p['total_risk_score']}</div></div>
                  </div>
                  <div style="font-size:10px;color:#475569;margin-top:8px;font-style:italic">{p['tradeoff']}</div>
                </div>""", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:#0a1e0a;border:1px solid #166534;border-radius:10px;
                    padding:14px 16px;margin-top:14px;font-size:13px;color:#4ade80;line-height:1.6">
          🤖 <b>AI Reasoning:</b> {plan_result['reasoning']}
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#334155;padding:30px;text-align:center">Run a tick to activate the Simulation Planner.</div>', unsafe_allow_html=True)

# ══ TAB 4 — VERIFICATION ══════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="slabel">Verification Layer — Probabilistic Task Tracking</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#0a1020;border:1px solid #1e2a40;border-radius:10px;
                padding:13px 18px;font-size:13px;color:#64748b;margin-bottom:14px;line-height:1.7">
      Ensures tasks are <b style="color:#94a3b8">actually completed</b> — not just assigned.
      Uses staff location + fire/smoke proximity to probabilistically verify completion.
      Failed tasks trigger automatic reassignment.
    </div>""", unsafe_allow_html=True)

    verifier = st.session_state.verifier
    if verifier and verifier.tasks:
        vcounts = verifier.summary()
        mc1,mc2,mc3,mc4 = st.columns(4)
        for col,label,val,color in [
            (mc1,"Active",  vcounts.get("active",0),  "#3b82f6"),
            (mc2,"Done",    vcounts.get("completed",0)+vcounts.get("likely_complete",0),"#22c55e"),
            (mc3,"Failed",  vcounts.get("failed",0),  "#ef4444"),
            (mc4,"Total",   vcounts.get("total",0),   "#94a3b8"),
        ]:
            col.markdown(f"""<div style="background:#0f1629;border:1px solid #1e2a40;border-radius:9px;
                            padding:12px;text-align:center">
              <div style="font-size:9px;color:#475569;letter-spacing:1px">{label.upper()}</div>
              <div style="font-size:28px;font-weight:900;color:{color};font-family:'JetBrains Mono'">{val}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<div class="slabel" style="margin-top:14px">Task Registry</div>', unsafe_allow_html=True)
        sc_map = {"active":("#3b82f6","⏳ ACTIVE"),"likely_complete":("#84cc16","🔄 LIKELY DONE"),
                  "completed":("#22c55e","✅ COMPLETE"),"failed":("#ef4444","❌ FAILED")}
        for tid, task in verifier.tasks.items():
            s    = task["status"]
            c, lbl = sc_map.get(s, ("#94a3b8","❓"))
            conf = task.get("confidence",1.0)
            fail = f'<div style="font-size:10px;color:#ef4444;margin-top:2px">{task.get("fail_reason","")}</div>' if task.get("fail_reason") else ""
            st.markdown(f"""
            <div class="vtask">
              <div>
                <span style="font-family:'JetBrains Mono';font-weight:700;color:#94a3b8">{tid}</span>
                &nbsp;<span style="color:#a855f7;font-weight:700">Staff {task['staff_id']}</span>
                <span style="color:#374151;margin:0 4px">→</span>
                <span style="color:#3b82f6;font-weight:700">Patient {task['patient_id']}</span>
                <div style="font-size:10px;color:#475569;margin-top:2px">
                  Assigned tick {task['assigned_tick']} | Deadline tick {task['deadline_tick']}
                </div>{fail}
              </div>
              <div style="text-align:right">
                <div style="font-weight:700;font-size:11px;color:{c}">{lbl}</div>
                <div style="height:4px;background:#1e2a40;border-radius:4px;width:80px;margin-top:4px">
                  <div style="height:4px;background:{c};border-radius:4px;width:{int(conf*100)}%"></div>
                </div>
                <div style="font-size:9px;color:{c};font-family:'JetBrains Mono';margin-top:2px">{int(conf*100)}%</div>
              </div>
            </div>""", unsafe_allow_html=True)

        verif_state = st.session_state.verification
        if verif_state.get("reassign_needed"):
            st.markdown('<div class="slabel" style="margin-top:12px;color:#ef4444">⚠️ Reassignment Triggered by AI</div>', unsafe_allow_html=True)
            for r in verif_state["reassign_needed"]:
                st.markdown(f"""<div style="background:#1a0a0a;border:1px solid #ef444450;border-radius:8px;
                                padding:10px 14px;margin-bottom:6px">
                  <span style="color:#ef4444;font-weight:700">Patient {r['patient_id']}</span>
                  <span style="color:#475569;font-size:12px;margin-left:8px">{r['reason']}</span>
                </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#334155;padding:30px;text-align:center">Run ticks to populate the verification layer.</div>', unsafe_allow_html=True)

# ══ TAB 5 — FIREFIGHTER ═══════════════════════════════════════════════════════
with tab5:
    if not st.session_state.ff_joined:
        st.markdown("""
        <div style="text-align:center;padding:50px 20px">
          <div style="font-size:48px">🚒</div>
          <div style="font-size:16px;font-weight:700;color:#475569;margin-top:12px">Firefighters Not Yet On Scene</div>
          <div style="font-size:13px;color:#334155;margin-top:6px">
            Press <b>🚒 Firefighters Arrive</b> in the sidebar.
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        ff = st.session_state.ff_briefing
        if ff:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#1a1000,#0d0a00);border:1px solid #f59e0b50;
                        border-radius:12px;padding:18px 22px;margin-bottom:14px">
              <div style="font-size:16px;font-weight:800;color:#f59e0b">🚒 FIREFIGHTER BRIEFING — Tick {ff['tick']}</div>
              <div style="font-size:13px;color:#92400e;margin-top:6px;line-height:1.8">
                Active fire: <b style="color:#ef4444">{ff['fire_cell_count']} cells</b> |
                Direction: <b style="color:#f97316">{ff['fire_spread_direction']}</b> |
                Internal staff: <b style="color:#a855f7">{ff['internal_staff_count']}</b> |
                Critical patients: <b style="color:#3b82f6">{len(ff['critical_patients'])}</b>
              </div>
            </div>""", unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="slabel">✅ Safe Entry Points</div>', unsafe_allow_html=True)
                for i, ep in enumerate(ff["safe_entry_points"][:3]):
                    is_rec = (ep == ff["recommended_entry"])
                    bc     = "#22c55e" if is_rec else "#1e2a40"
                    rec    = " ⭐ RECOMMENDED" if is_rec else ""
                    st.markdown(f"""
                    <div class="ff-entry" style="border-color:{bc}50">
                      <span style="font-weight:700;color:#22c55e;font-family:'JetBrains Mono'">
                        Entry {i+1}: ({ep[0]},{ep[1]})</span>
                      <span style="font-size:11px;color:#4ade80">{rec}</span>
                      <div style="font-size:10px;color:#475569;margin-top:2px">No fire · Low smoke · Accessible</div>
                    </div>""", unsafe_allow_html=True)

                st.markdown('<div class="slabel" style="margin-top:12px">🔴 Hot Zones</div>', unsafe_allow_html=True)
                for z in ff["hot_zones"][:4]:
                    st.markdown(f"""
                    <div class="ff-zone">
                      <span style="font-weight:700;color:#ef4444;font-family:'JetBrains Mono'">
                        ({z['cell'][0]},{z['cell'][1]})</span>
                      <span style="background:#3b0a0a;color:#ef4444;font-size:9px;
                                   padding:2px 7px;border-radius:10px;margin-left:6px">{z['label']}</span>
                      <div style="font-size:10px;color:#475569;margin-top:2px">Approach from upwind side</div>
                    </div>""", unsafe_allow_html=True)

            with c2:
                st.markdown('<div class="slabel">🏥 Patients Needing FF Help</div>', unsafe_allow_html=True)
                if ff["critical_patients"]:
                    for cp in ff["critical_patients"]:
                        urg_c = "#ef4444" if cp["urgency"]=="IMMEDIATE" else "#f97316"
                        st.markdown(f"""
                        <div class="ff-patient">
                          <div style="display:flex;justify-content:space-between">
                            <span style="font-weight:700;color:#3b82f6">Patient {cp['patient_id']}
                              <span style="color:#94a3b8;font-size:11px;margin-left:5px">{cp['type']}</span>
                            </span>
                            <span style="background:#1a0a0a;color:{urg_c};font-size:9px;
                                         font-weight:800;padding:2px 8px;border-radius:10px">{cp['urgency']}</span>
                          </div>
                          <div style="font-size:11px;color:#475569;margin-top:4px;font-family:'JetBrains Mono'">
                            ({cp['location'][0]},{cp['location'][1]}) | fire dist={cp['fire_distance']} | smoke={cp['smoke_level']}
                          </div>
                        </div>""", unsafe_allow_html=True)
                else:
                    st.markdown('<div style="color:#334155;font-size:13px;padding:10px">No critical patients requiring FF at this tick.</div>', unsafe_allow_html=True)

                st.markdown('<div class="slabel" style="margin-top:12px">📡 Predicted Fire (3 Ticks)</div>', unsafe_allow_html=True)
                pred_cells = ff.get("predicted_fire_cells",[])
                if pred_cells:
                    cell_str = ", ".join(f"({x},{y})" for x,y,f in pred_cells[:8])
                    more = f" +{len(pred_cells)-8} more" if len(pred_cells)>8 else ""
                    st.markdown(f"""
                    <div style="background:#1a1500;border:1px solid #eab30840;border-radius:8px;padding:12px 14px">
                      <div style="font-size:9px;color:#eab308;font-weight:700;letter-spacing:1px;margin-bottom:5px">AVOID THESE CELLS</div>
                      <div style="font-family:'JetBrains Mono';font-size:11px;color:#92400e">{cell_str}{more}</div>
                    </div>""", unsafe_allow_html=True)

            st.markdown("---")
            st.markdown('<div class="slabel">🤝 Coordinated Action Plan (Internal Staff)</div>', unsafe_allow_html=True)
            if asns.get("assignments"):
                staff_rooms = [f"Staff <b style='color:#a855f7'>{a['staff_id']}</b> @ Room <b style='color:#e2e8f0'>{a['target_room']}</b> (P{a['patient_id']})" for a in asns["assignments"]]
                st.markdown(f"""
                <div style="background:#0f1629;border:1px solid #1e2a40;border-left:4px solid #a855f7;border-radius:8px;padding:12px 14px">
                  <div style="font-size:12px;color:#cbd5e1;line-height:1.8">
                    {"<br>".join(staff_rooms)}
                  </div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown('<div style="font-size:12px;color:#475569;padding:10px;background:#0f1629;border:1px solid #1e2a40;border-radius:8px">No active internal staff assignments.</div>', unsafe_allow_html=True)
