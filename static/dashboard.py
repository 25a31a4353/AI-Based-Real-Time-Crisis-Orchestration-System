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
.stApp{background:#090d17;overflow:visible!important;}
.block-container{padding:2.5rem 1.8rem 2rem!important;max-width:100%!important;overflow:visible!important;}
button[data-testid="baseButton-primary"]{background:linear-gradient(135deg,#ef4444,#b91c1c)!important;border:none!important;color:#fff!important;font-weight:700!important;}
button[data-testid="baseButton-secondary"]{background:#151c2c!important;border:1px solid #2a3348!important;color:#cbd5e1!important;font-weight:600!important;}
.hdr{background:linear-gradient(135deg,#0f1629,#0a0f1e);border:1px solid #1e2a40;border-radius:14px;padding:18px 26px;margin-bottom:16px;display:flex;align-items:center;justify-content:space-between;position:relative;}
@media (max-width: 768px) { .team-badge-header { display: none !important; } }
.hdr-title{font-size:20px;font-weight:900;color:#f1f5f9;letter-spacing:-.3px;}
.hdr-sub{font-size:12px;color:#475569;margin-top:3px;}
.badge-live{background:#ef4444;color:#fff;font-size:10px;font-weight:800;padding:3px 10px;border-radius:20px;letter-spacing:1px;animation:pulse 1.6s infinite;}
.badge-tick{background:#1e2a40;color:#94a3b8;font-size:11px;font-weight:700;padding:4px 12px;border-radius:20px;font-family:'JetBrains Mono';}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.55}}
@keyframes fadeInEvent{from{opacity:0;transform:translateX(-10px);}to{opacity:1;transform:translateX(0);}}
.story-row{display:flex;align-items:flex-start;gap:12px;margin-bottom:10px;padding-bottom:10px;border-bottom:1px solid #1e2a40;animation:fadeInEvent 0.4s ease-out;}
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
.gc-pred{background:#2d2000;border:2px solid #eab308!important;box-shadow:0 0 8px #eab30860;animation:fireWarning 1.2s infinite;}
@keyframes fireWarning{0%,100%{opacity:0.6;}50%{opacity:1;box-shadow:0 0 12px #eab308;}}
.priority-badge{position:absolute;top:2px;right:2px;width:8px;height:8px;border-radius:50%;border:1px solid rgba(255,255,255,.3);}
.badge-critical{background:#ef4444;box-shadow:0 0 6px #ef4444;}
.badge-high{background:#f97316;}
.badge-medium{background:#84cc16;}
.badge-low{background:#64748b;}
.gc-smoke{background:#1f1500;border-color:#92400e;}
.gc-new-fire{animation:fireSpread 0.8s ease-out;}
@keyframes fireSpread{0%{background-color:#3b0a0a;box-shadow:0 0 4px #ef4444;transform:scale(0.8);}50%{box-shadow:0 0 12px #ff6b6b;}100%{background-color:#5a0000;box-shadow:0 0 16px #ff6b6b,inset 0 0 8px #ef4444;transform:scale(1);}}
.decision-flash{animation:decisionHighlight 0.6s ease-in-out;}
@keyframes decisionHighlight{0%{background:inherit;}50%{background:#22c55e30;box-shadow:0 0 12px #22c55e60;}100%{background:inherit;}}
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
        initial_risk=None,     # baseline risk at tick 0 for reduction metric
        timeline=[],           # rich narrative timeline events
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

    # ── CRISIS TIMELINE & VOICE ALERTS ────────────────────────────────────────
    events = []
    t_val = sim.tick
    if "pending_voice_alerts" not in st.session_state:
        st.session_state.pending_voice_alerts = []

    # 1. Fire Events
    if len(fire_after) > len(fire_before):
        new_count = len(fire_after) - len(fire_before)
        events.append({"tick": t_val, "icon": "🔥", "color": "#ef4444", "msg": f"Fire spread detected — {new_count} new cells ignited."})
        
        # Determine sector
        fire_sector = "the building"
        if ff_briefing and ff_briefing.get("fire_spread_direction"):
            fire_sector = ff_briefing["fire_spread_direction"]
        st.session_state.pending_voice_alerts.append(f"Fire detected in sector {fire_sector}")
    
    # 2. Patient & AI Events
    if decisions:
        for d in decisions:
            pid = d["patient_id"]
            np  = d["priority"]
            op  = prev.get(pid)
            lvl = d["explanation"]["priority_level"]
            if op and np > op + 1.0 and lvl == "critical":
                events.append({"tick": t_val, "icon": "🏥", "color": "#ef4444", "msg": f"Patient {pid} risk increased to CRITICAL due to environment."})
                st.session_state.pending_voice_alerts.append(f"Patient {pid} priority elevated to critical")

        if plan and plan.get("recommended_plan"):
            p_name = plan["recommended_plan"]["name"]
            prev_plan = st.session_state.get("prev_plan_name")
            surv = plan["recommended_plan"]["survival_probability"]
            events.append({"tick": t_val, "icon": "🤖", "color": "#22c55e", "msg": f"AI selected '{p_name}' — {surv}% survival probability."})
            if p_name != prev_plan and prev_plan is not None:
                st.session_state.pending_voice_alerts.append(f"AI activated {p_name} strategy")
            st.session_state.prev_plan_name = p_name

    # 3. Staff Events
    if assignments.get("assignments"):
        for a in assignments["assignments"]:
            pid = a["patient_id"]
            sid = a["staff_id"]
            if "rerouted" in a.get("route_note", "").lower():
                events.append({"tick": t_val, "icon": "👷", "color": "#a855f7", "msg": f"Staff {sid} rerouted due to fire obstruction."})
            elif t_val == a.get("assigned_tick", t_val):
                events.append({"tick": t_val, "icon": "👷", "color": "#a855f7", "msg": f"Staff {sid} assigned to Patient {pid} — route clear."})

    # 4. Verification Events
    for tid, t in verif.tasks.items():
        if t["status"] in ("completed", "likely_complete") and t_val == t.get("completed_tick", t_val):
            events.append({"tick": t_val, "icon": "✅", "color": "#22c55e", "msg": f"Task {tid} completed — Patient {t['patient_id']} rescue verified."})
            st.session_state.pending_voice_alerts.append("Patient evacuation complete")
        elif t["status"] == "failed" and t_val == t.get("failed_tick", t_val):
            events.append({"tick": t_val, "icon": "❌", "color": "#ef4444", "msg": f"Task {tid} failed — deadline exceeded, triggering reassignment."})

    # 5. Firefighter Events
    ff_joined_prev = st.session_state.get("ff_joined", False)
    if sim.firefighters and not ff_joined_prev:
        st.session_state.pending_voice_alerts.append("Firefighters arrived at entry point alpha")
        st.session_state.ff_joined = True

    if ff_briefing and len(ff_briefing.get("critical_patients", [])) > 0:
        if t_val % 3 == 0:  # Prevent spamming every tick
            events.append({"tick": t_val, "icon": "🚒", "color": "#f59e0b", "msg": f"Firefighter briefing updated — {len(ff_briefing['critical_patients'])} critical patients identified."})

    st.session_state.timeline.extend(events)

# ── Grid renderer ─────────────────────────────────────────────────────────────
_priority_map = {}   # module-level, set by render_grid each call
def render_grid(sim, floor=0, predicted_fire=None, fire_new_cells=None, priority_map=None):
    global _priority_map
    _priority_map = priority_map or {}
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
            badge_html = ""
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
                lvl  = _priority_map.get(p.id, "low")
                badge_html = f'<span class="priority-badge badge-{lvl}"></span>'
            elif pos in pred2d:
                icon = "⚠️"; cls = "gc-pred"   # predicted fire
            elif sim.smoke_map[floor][y][x] > 0.35:
                icon = "💨"; cls = "gc-smoke"   # smoke
            elif pos in exits:
                icon = "🚪"; cls = "gc-exit"
            else:
                icon = ""; cls = "gc-empty"
            html += f'<div class="gc {cls}{extra_cls}" title="{x},{y}">{icon}{badge_html}<span class="coord">{x},{y}</span></div>'
        html += '</div>'
    html += '''</div>
    <div class="legend">
      <div class="li"><div class="ld" style="background:#ff6b6b"></div>Fire (intense)</div>
      <div class="li"><div class="ld" style="background:#ef4444"></div>Fire</div>
      <div class="li"><div class="ld" style="background:#eab308;border:1px solid #eab308"></div>⚠️ Predicted (3 ticks)</div>
      <div class="li"><div class="ld" style="background:#92400e"></div>💨 Smoke</div>
      <div class="li"><div class="ld" style="background:#3b82f6"></div>ICU Patient</div>
      <div class="li"><div class="ld" style="background:#22c55e"></div>Mobile Patient</div>
      <div class="li"><div class="ld" style="background:#a855f7"></div>Staff</div>
      <div class="li"><div class="ld" style="background:#f59e0b"></div>Firefighter</div>
      <div class="li"><div class="ld" style="background:#4ade80"></div>Exit</div>
      <div class="li"><div class="ld" style="background:#ef4444;border-radius:50%"></div>● Critical</div>
      <div class="li"><div class="ld" style="background:#f97316;border-radius:50%"></div>● High</div>
    </div></div>'''
    return html


def render_priorities(decisions, patients, prev_decisions=None):
    mob_map = {p.id: p.movable for p in patients}
    cc  = {"critical":"#ef4444","high":"#f97316","medium":"#84cc16","low":"#475569"}
    bcl = {"critical":"bc","high":"bh","medium":"bm","low":"bl"}
    html = ""
    max_s = max((d["priority"] for d in decisions), default=1) or 1
    prev = prev_decisions or {}
    
    for d in decisions:
        pid = d["patient_id"]; s = d["priority"]
        lvl = d["explanation"]["priority_level"]
        mob = "Mobile" if mob_map.get(pid, True) else "ICU — Immobile"
        c   = cc.get(lvl, "#475569")
        pct = int(s/max_s*100)
        ff  = d.get("predicted_fire_nearby")
        warn= ' <span style="color:#eab308;font-size:10px">⚠️ predicted fire</span>' if ff else ""
        
        flash_cls = " decision-flash" if prev.get(pid) != s else ""
        
        html += f"""
        <div class="pcard{flash_cls}" style="border-left-color:{c}">
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

def render_assignments(assignments_data, prev_assignments=None):
    html = ""
    prev_asns = prev_assignments or {}
    for a in assignments_data.get("assignments", []):
        sid = a['staff_id']
        note = a.get("route_note","")
        ncls = "color:#22c55e" if "✅" in note else "color:#f97316"
        bd   = a.get("cost_breakdown",{})
        
        # Check if new assignment or changed patient target
        flash_cls = ""
        if prev_asns.get(sid) != a['patient_id']:
            flash_cls = " decision-flash"
            
        html += f"""
        <div class="acard{flash_cls}">
          <div style="display:flex;align-items:center;gap:8px">
            <span class="afrom">Staff {sid}</span>
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


def build_live_reasoning(decisions, assignments_data, sim, plan_result, prev_decisions=None):
    """Generate 4-6 plain-English bullets for the AI DECISION ENGINE panel."""
    bullets = []
    prev = prev_decisions or {}
    fire_cells = list(sim.fire)

    # 1. Fire status
    if fire_cells:
        cx = sum(x for x,y,*_ in fire_cells)/len(fire_cells)
        cy = sum(y for x,y,*_ in fire_cells)/len(fire_cells)
        if len(fire_cells) >= 4:
            rc = fire_cells[-max(4,len(fire_cells)//4):]
            rcx = sum(x for x,y,*_ in rc)/len(rc); rcy = sum(y for x,y,*_ in rc)/len(rc)
            hd = "East" if rcx>cx+0.3 else ("West" if rcx<cx-0.3 else "")
            vd = "South" if rcy>cy+0.3 else ("North" if rcy<cy-0.3 else "")
            dirn = (f"{vd}-{hd}").strip("-") or "RADIAL"
        else:
            dirn = "RADIAL"
        sv = list(sim.fire_severity.values())
        slo,shi = (min(sv),max(sv)) if sv else (1,1)
        bullets.append(f"🔥 Fire spreading <b>{dirn}</b> from centroid ({round(cx,1)},{round(cy,1)}) — <b>{len(fire_cells)}</b> cells active, severity {slo}–{shi}")
    else:
        bullets.append("🔥 No active fire cells at this tick.")

    # 2. Predicted expansion
    predicted = sim.predict_fire_spread(3) if sim.fire else []
    if predicted:
        samp = ", ".join(f"({x},{y})" for x,y,*_ in predicted[:4])
        more = f" +{len(predicted)-4} more" if len(predicted)>4 else ""
        bullets.append(f"📊 Predicted expansion: <b>{len(predicted)}</b> new cells in 3 ticks → {samp}{more}")

    # 3. Top patient risk delta
    if decisions:
        top=decisions[0]; pid=top["patient_id"]; new_s=top["priority"]; old_s=prev.get(pid)
        e=top["explanation"]
        rs=[]
        if e["smoke_level"]>0.3: rs.append(f"smoke {e['smoke_level']:.2f}")
        if e["min_fire_dist"]<=3: rs.append(f"fire {e['min_fire_dist']} cells away")
        if top["is_icu"]: rs.append("ICU/immobile")
        reason = " & ".join(rs) if rs else "combined risk"
        if old_s and abs(new_s-old_s)>=1.0:
            pct=round(abs(new_s-old_s)/max(old_s,1)*100)
            word="increased" if new_s>old_s else "decreased"
            bullets.append(f"⚠️ Patient <b>{pid}</b> risk <b>{word}</b> by {pct}% due to {reason}")
        else:
            bullets.append(f"⚠️ Patient <b>{pid}</b> highest priority (score <b>{new_s}</b>) — {reason}")

    # 4. Staff assignment reasoning
    alist = assignments_data.get("assignments",[])
    if alist:
        rerouted=[a for a in alist if "rerouted" in a.get("route_note","").lower()]
        a = rerouted[0] if rerouted else alist[0]
        bd=a.get("cost_breakdown",{})
        if rerouted:
            bullets.append(f"🎯 AI rerouted Staff <b>{a['staff_id']}</b> → Patient <b>{a['patient_id']}</b> (fire blocked path, cost={bd.get('total_cost','?')})")
        else:
            bullets.append(f"🎯 AI assigned Staff <b>{a['staff_id']}</b> → Patient <b>{a['patient_id']}</b> (dist={bd.get('distance','?')}, skill_bonus={bd.get('skill_bonus',0)})")

    # 5. Route ETA
    if alist:
        clear=[a for a in alist if "✅" in a.get("route_note","")]
        rr=[a for a in alist if "rerouted" in a.get("route_note","").lower()]
        if clear:
            a=clear[0]; eta=int(a.get("cost_breakdown",{}).get("distance",2))
            bullets.append(f"✅ Staff <b>{a['staff_id']}</b> route clear — ETA <b>{eta}</b> ticks to Patient <b>{a['patient_id']}</b>")
        elif rr:
            a=rr[0]
            bullets.append(f"⚠️ Staff <b>{a['staff_id']}</b> rerouted — fire blocked direct path to Patient <b>{a['patient_id']}</b>")

    # 6. Planner
    if plan_result and plan_result.get("recommended_plan"):
        p=plan_result["recommended_plan"]
        others=[r for r in plan_result.get("plans",[]) if not r.get("recommended")]
        vs=" vs ".join(f"{o['name']} ({o['survival_probability']}%)" for o in others)
        bullets.append(f"🤖 AI Planner selected '<b>{p['name']}</b>' — <b>{p['survival_probability']}%</b> survival" + (f" vs {vs}" if vs else ""))

    return bullets[:6]


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-size:17px;font-weight:900;color:#f1f5f9;margin-bottom:2px">⚡ CrisisAI</div>', unsafe_allow_html=True)
    
    st.markdown('<div style="font-size:11px;color:#22c55e;font-weight:800;letter-spacing:1px;margin-bottom:8px;margin-top:10px;">🏗️ SYSTEM ARCHITECTURE</div>', unsafe_allow_html=True)
    
    with st.expander("📡 CONNECTED DATA SOURCES", expanded=False):
        st.markdown("""
        <div style="background:#0f1629;border-radius:10px;padding:12px 14px;margin-bottom:8px;border:1px solid #1e2a40;">
            <div style="font-weight:bold;font-size:13px;margin-bottom:4px;color:#e2e8f0;">🌡️ THERMAL SENSORS</div>
            <div style="font-size:11px;color:#94a3b8;line-height:1.4;">
                Building IoT network monitoring temperature<br>
                • 50+ sensors per floor<br>
                • Real-time feed via MQTT protocol<br>
                • Detection: Temperature > 55°C = fire risk
            </div>
        </div>
        <div style="background:#0f1629;border-radius:10px;padding:12px 14px;margin-bottom:8px;border:1px solid #1e2a40;">
            <div style="font-weight:bold;font-size:13px;margin-bottom:4px;color:#e2e8f0;">📹 SMOKE DETECTION (CCTV AI)</div>
            <div style="font-size:11px;color:#94a3b8;line-height:1.4;">
                Computer vision on existing CCTV feeds<br>
                • Pixel density analysis for smoke plumes<br>
                • Connected via secure API<br>
                • Updates simulation smoke map
            </div>
        </div>
        <div style="background:#0f1629;border-radius:10px;padding:12px 14px;margin-bottom:8px;border:1px solid #1e2a40;">
            <div style="font-weight:bold;font-size:13px;margin-bottom:4px;color:#e2e8f0;">📍 LOCATION TRACKING</div>
            <div style="font-size:11px;color:#94a3b8;line-height:1.4;">
                Staff & patient location (beacon/WiFi)<br>
                • Staff: RFID badges<br>
                • Patients: Wearable proximity sensors<br>
                • Updates staff/patient positions real-time
            </div>
        </div>
        <div style="background:#0f1629;border-radius:10px;padding:12px 14px;border:1px solid #1e2a40;">
            <div style="font-weight:bold;font-size:13px;margin-bottom:4px;color:#e2e8f0;">🚨 BUILDING MANAGEMENT (BMS)</div>
            <div style="font-size:11px;color:#94a3b8;line-height:1.4;">
                Fire alarm + door control integration<br>
                • Sprinkler system status<br>
                • Door unlock commands from AI<br>
                • Fire compartmentalization feedback
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with st.expander("⚙️ AI ORCHESTRATION ENGINE", expanded=False):
        st.markdown("""
        <div style="font-family:'JetBrains Mono', monospace; font-size:10px; color:#cbd5e1; background:#0a0f1e; padding:10px; border-radius:8px; border:1px solid #1e2a40; white-space:pre; overflow-x:auto;">
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  DETECTION   │→ │   DECISION   │→ │ ASSIGNMENT   │
│              │  │              │  │              │
│ Real-time    │  │ Hybrid AI:   │  │ Optimal route│
│ hazard ID    │  │ rule-based + │  │ planning     │
│ Temp/smoke   │  │ predictive   │  │ Staff → Pat  │
│ Fire spread  │  │ simulation   │  │              │
│              │  │              │  │              │
│              │  │ Gemini LLM:  │  │              │
│              │  │ Explainabil. │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
                         |
                 ┌───────▼────────┐
                 │  VERIFICATION  │
                 │                │
                 │ Real-time task │
                 │ tracking       │
                 │ Success metrics│
                 └────────────────┘
        </div>
        """, unsafe_allow_html=True)



    with st.expander("🏥 FUTURE SCOPE", expanded=False):
        st.markdown("""
        <div style="font-size:11px;color:#cbd5e1;line-height:1.5;">
            <b>CrisisAI will integrate into typical multi-occupancy buildings</b> (hospitals, offices, data centers, schools) with:<br><br>
            <b style="color:#e2e8f0">SENSORS TO BE DEPLOYED:</b><br>
            - Thermal: 50-200 sensors will monitor building floors<br>
            - Smoke detection: AI-powered CCTV systems will be implemented<br>
            - Staff location: RFID badges will track responder movement<br>
            - Patient tracking: Wearable proximity sensors will be assigned<br><br>
            <b style="color:#e2e8f0">FUTURE SYSTEM ACTIVATION:</b><br>
            - Thermal sensors will detect temp > 55°C → alerts will be sent to the API<br>
            - AI will process building states and identify available responders<br>
            - AI will decide: Which patients to evacuate, which staff to dispatch, and which plan will give the highest survival %<br>
            - System will send commands: Unlock safe exits, alert staff, and notify fire departments.<br><br>
            <b style="color:#e2e8f0">SCALE GOALS:</b><br>
            - Single building: Real-time management for up to 500 occupants<br>
            - Multi-building: Parallel instances will run per building<br>
            - City-level: A microservices cluster will coordinate city-wide responses<br><br>
            <b style="color:#e2e8f0">TARGET DEPLOYMENTS:</b><br>
            - Hospital ICU wards (250+ patients)<br>
            - Office complexes (500+ employees)<br>
            - University campuses (10,000+ daily occupants)
        </div>
        """, unsafe_allow_html=True)
        
    @st.dialog("Future Deployment Guide")
    def show_deployment_guide():
        st.markdown("### CrisisAI Technical Architecture & Deployment Guide")
        st.markdown("This guide provides the complete technical specifications for deploying CrisisAI in a real-world multi-occupancy building environment.")
        st.markdown("""
        #### Architecture Overview
        CrisisAI is designed as a cloud-native microservices architecture, communicating over secure REST APIs and real-time WebSockets.
        
        #### Hardware Requirements (On-Premise Edge Node)
        For locations with unreliable internet access, CrisisAI supports edge deployment.
        - **Compute:** NVIDIA Jetson Orin (for local CCTV smoke detection) or standard x86 server (16GB RAM, 8 cores).
        - **Network:** Redundant dual-WAN routers with cellular backup (4G/5G).
        
        #### Software Stack
        - **Backend Orchestrator:** Python / FastAPI
        - **Real-time Interface:** Streamlit / React Custom Components
        - **Message Broker:** Eclipse Mosquitto (MQTT) for IoT telemetry
        - **Simulation Core:** Custom optimized Python A* pathfinding and cellular automata
        
        #### Integration Interfaces
        - **BMS API Interface:** Uses standard protocols (BACnet/IP, Modbus TCP) via a gateway to interact with building systems (HVAC, Elevators, Fire Doors).
        - **Communication Gateway:** Twilio API for SMS/Voice broadcasts to staff phones, integration with existing pager systems.
        - **CCTV Integration:** RTSP streams ingested into a lightweight OpenCV/YOLOv8 pipeline for smoke pattern recognition.
        """)

    if st.button("🔗 Future Deployment Guide", key="deploy_guide_btn", use_container_width=True):
        show_deployment_guide()

    st.markdown("---")
    st.markdown('<div style="font-size:11px;color:#22c55e;font-weight:800;letter-spacing:1px;margin-bottom:8px;margin-top:10px;">⚙️ CONTROL PANEL</div>', unsafe_allow_html=True)

    with st.expander("🏗️ Building Architecture", expanded=False):
        grid_w    = st.slider("Width (rooms)", 6, 15, 10)
        grid_h    = st.slider("Height (rooms)", 6, 15, 10)
        floors    = st.slider("Floors", 1, 3, 1)

    with st.expander("👥 Occupant Demographics", expanded=False):
        num_pat   = st.slider("Total patients", 2, 12, 5)
        num_icu   = st.slider("ICU (immobile)", 0, num_pat, 2)
        num_staff = st.slider("Staff members", 1, 6, 3)
        num_train = st.slider("Trained medics", 0, num_staff, 2)

    with st.expander("🔥 Hazard Simulation Limits", expanded=False):
        fire_x    = st.slider("Fire origin X", 0, grid_w-1, grid_w//2)
        fire_y    = st.slider("Fire origin Y", 0, grid_h-1, grid_h//2)
        fire_fl   = st.slider("Fire floor", 0, floors-1, 0) if floors > 1 else 0
        fire_spd  = st.select_slider("Fire speed", ["Slow","Normal","Fast"], value="Normal")
        spd_map   = {"Slow":1,"Normal":1,"Fast":2}

    with st.expander("🔊 System Integrations", expanded=False):
        voice_enabled = st.toggle("Enable Voice Alerts (PA System)", value=False)
        st.session_state.voice_alerts = voice_enabled
    
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
        st.session_state.timeline    = []
        st.session_state.ff_joined   = False
        st.session_state.initialized = True
        st.session_state.view_floor  = 0
        st.session_state.initial_risk= None
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
            st.session_state.timeline.append({"tick": sim.tick, "icon": "🚒", "color": "#f59e0b", "msg": f"Firefighters arrived — {len(entries[:2])} units deployed at safe entries."})
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

    st.markdown("""
    <div style="background:#0a0f1e; border-top:2px solid #1e2a40; padding:16px 14px; margin-top:20px; border-radius:0 0 12px 12px;">
      <div style="font-size:9px; font-weight:800; color:#64748b; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:12px;">
        👥 TEAM INFORMATION
      </div>
      <div style="background:#1e2a40; border-radius:12px; padding:4px 10px; display:inline-block; margin-bottom:16px;">
        <span style="font-size:10px; font-weight:700; color:#ffffff;">🎓 Pragati Engineering College</span>
      </div>
      <!-- Leader -->
      <div style="display:flex; align-items:flex-start; margin-bottom:8px; border-left:2px solid #eab308; padding-left:8px;">
        <div style="flex-grow:1;">
          <div style="font-size:11px; font-weight:700; color:#eab308; display:flex; align-items:center; gap:6px;">
            ⭐ Shanmukheswar Medicharla <span style="background:#eab308; color:#000; font-size:8px; font-weight:800; padding:1px 6px; border-radius:10px;">TEAM LEADER</span>
          </div>
          <div style="font-size:9px; color:#64748b; font-family:'JetBrains Mono'; user-select:none;">shanmukheswaramedicharla9604@gmail.com</div>
        </div>
      </div>
      <!-- Member 2 -->
      <div style="display:flex; align-items:flex-start; margin-bottom:8px; padding-left:10px;">
        <div style="flex-grow:1;">
          <div style="font-size:11px; font-weight:700; color:#ffffff;">👤 Vedavyas Borra</div>
          <div style="font-size:9px; color:#64748b; font-family:'JetBrains Mono'; user-select:none;">vedavyasborra@gmail.com</div>
        </div>
      </div>
      <!-- Member 3 -->
      <div style="display:flex; align-items:flex-start; margin-bottom:8px; padding-left:10px;">
        <div style="flex-grow:1;">
          <div style="font-size:11px; font-weight:700; color:#ffffff;">👤 Kota Pardhasaradhi</div>
          <div style="font-size:9px; color:#64748b; font-family:'JetBrains Mono'; user-select:none;">kotapardhasaradhi5@gmail.com</div>
        </div>
      </div>
      <!-- Member 4 -->
      <div style="display:flex; align-items:flex-start; margin-bottom:8px; padding-left:10px;">
        <div style="flex-grow:1;">
          <div style="font-size:11px; font-weight:700; color:#ffffff;">👤 Harshith Kotha</div>
          <div style="font-size:9px; color:#64748b; font-family:'JetBrains Mono'; user-select:none;">kothaharshith75@gmail.com</div>
        </div>
      </div>
      <div style="text-align:center; font-size:9px; font-style:italic; color:#475569; margin-top:16px;">
        Built for Google Solution Challenge 2025
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── Impact Metrics Banner ─────────────────────────────────────────────────────
_sim = st.session_state.get("sim")
_decs = st.session_state.get("decisions", [])
_plan = st.session_state.get("plan")
_verif = st.session_state.get("verifier")

# 1. Patients Rescued
rescued = 0
total_p = len(_sim.patients) if _sim else 0
if _sim:
    completed_pids = set()
    if _verif:
        for t in _verif.tasks.values():
            if t["status"] in ("completed", "likely_complete"):
                completed_pids.add(t["patient_id"])
    for p in _sim.patients:
        if getattr(p, "evacuated", False) or p.id in completed_pids:
            rescued += 1
pct_rescued = round((rescued / total_p * 100) if total_p > 0 else 0, 1)

# 2. Risk Reduction
current_risk = sum(d.get("priority", 0) for d in _decs) if _decs else 0
if st.session_state.get("initial_risk") is None and current_risk > 0:
    st.session_state.initial_risk = current_risk
init_risk = st.session_state.get("initial_risk") or 0
if init_risk > 0:
    reduction = round(((init_risk - current_risk) / init_risk) * 100, 1)
    reduction = max(0.0, min(100.0, reduction))
else:
    reduction = 0.0

# 3. Response Time
avg_ticks_str = "N/A"
if _verif:
    completed_tasks = [t for t in _verif.tasks.values() if t["status"] in ("completed", "likely_complete")]
    if completed_tasks:
        diffs = [t.get("completed_tick", _sim.tick) - t["assigned_tick"] for t in completed_tasks]
        avg = sum(diffs) / len(diffs) if diffs else 0
        avg_ticks_str = f"{avg:.1f} ticks"

# 4. AI Efficiency
efficiency = "N/A"
if _plan and _plan.get("recommended_plan"):
    efficiency = f"{_plan['recommended_plan'].get('survival_probability', 'N/A')}%"

# Border Glow logic
b_color = "#22c55e" if pct_rescued >= 80 else ("#3b82f6" if pct_rescued >= 50 else "#f97316")

st.markdown(f"""
<div style="background:linear-gradient(135deg, #0c1120, #0a1e0a); border: 2px solid {b_color}; border-radius: 12px; padding: 16px 24px; margin-top: 12px; margin-bottom: 16px; display: flex; justify-content: space-between; flex-wrap: wrap; gap: 16px;">
  <!-- METRIC 1 -->
  <div style="flex: 1; min-width: 150px;">
    <div style="font-size: 10px; color: #22c55e; font-weight: 800; letter-spacing: 1px; margin-bottom: 4px;">🚑 PATIENTS RESCUED</div>
    <div style="font-size: 32px; font-weight: 900; color: #22c55e; font-family: 'JetBrains Mono', monospace; line-height: 1;">
      {rescued} / {total_p}
      <span style="font-size: 14px; color: #64748b; font-weight: 600; font-family: 'Inter', sans-serif;"> ({pct_rescued}%)</span>
    </div>
  </div>
  <!-- METRIC 2 -->
  <div style="flex: 1; min-width: 150px;">
    <div style="font-size: 10px; color: #3b82f6; font-weight: 800; letter-spacing: 1px; margin-bottom: 4px;">📉 TOTAL RISK REDUCTION</div>
    <div style="font-size: 32px; font-weight: 900; color: #3b82f6; font-family: 'JetBrains Mono', monospace; line-height: 1;">{reduction}%</div>
  </div>
  <!-- METRIC 3 -->
  <div style="flex: 1; min-width: 150px;">
    <div style="font-size: 10px; color: #eab308; font-weight: 800; letter-spacing: 1px; margin-bottom: 4px;">⚡ AVG RESPONSE TIME</div>
    <div style="font-size: 32px; font-weight: 900; color: #eab308; font-family: 'JetBrains Mono', monospace; line-height: 1;">{avg_ticks_str}</div>
  </div>
  <!-- METRIC 4 -->
  <div style="flex: 1; min-width: 150px;">
    <div style="font-size: 10px; color: #a855f7; font-weight: 800; letter-spacing: 1px; margin-bottom: 4px;">🎯 AI PLAN EFFICIENCY</div>
    <div style="font-size: 32px; font-weight: 900; color: #a855f7; font-family: 'JetBrains Mono', monospace; line-height: 1;">{efficiency}</div>
  </div>
</div>
""", unsafe_allow_html=True)



# ── Crisis Intensity & Voice Execution ────────────────────────────────────────
sim = st.session_state.get("sim")
_decs = st.session_state.get("decisions", [])
_verif = st.session_state.get("verifier")
if sim:
    tot_cap = sim.building.width * sim.building.height * sim.building.floors
    _crit_n = sum(1 for d in _decs if d["explanation"]["priority_level"]=="critical") if _decs else 0
    _fail_n = _verif.summary().get("failed", 0) if _verif else 0
    intensity = min(100.0, (len(sim.fire) * 10 + _crit_n * 15 + _fail_n * 20) / tot_cap * 100)
    
    meter_color = "#22c55e" if intensity <= 30 else ("#f59e0b" if intensity <= 60 else "#ef4444")
    st.markdown(f"""
    <div style="background:linear-gradient(135deg, #0f1629, #0a0f1e); border:1px solid #1e2a40; border-radius:12px; padding:12px 20px; margin-bottom:16px; display:flex; align-items:center; gap:16px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
      <div style="font-size:12px; font-weight:900; color:#94a3b8; letter-spacing:1px; min-width:140px;">⚠️ CRISIS INTENSITY</div>
      <div style="flex:1; background:#1e2a40; height:12px; border-radius:10px; overflow:hidden; position:relative; box-shadow:inset 0 1px 3px rgba(0,0,0,0.5);">
        <div style="width:{intensity}%; height:100%; background:{meter_color}; box-shadow:0 0 10px {meter_color}80; transition:width 0.5s ease-out, background 0.5s;"></div>
      </div>
      <div style="font-size:18px; font-weight:900; color:{meter_color}; font-family:'JetBrains Mono'; min-width:70px; text-align:right;">{intensity:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

if st.session_state.get("voice_alerts", False) and st.session_state.get("pending_voice_alerts"):
    js = "function speakAlert(msg){if(!window.speechSynthesis)return;let u=new SpeechSynthesisUtterance(msg);u.rate=1.0;u.pitch=1.0;u.volume=0.8;window.speechSynthesis.speak(u);}\n"
    for msg in st.session_state.pending_voice_alerts:
        js += f"speakAlert('{msg}');\n"
    st.components.v1.html(f"<script>{js}</script>", height=0)
    st.session_state.pending_voice_alerts = []

# ── Header ────────────────────────────────────────────────────────────────────
tick_val = st.session_state.sim.tick if st.session_state.sim else 0
st.markdown(f"""
<div class="hdr">
  <div>
    <div class="hdr-title">🔥 AI-Based Real-Time Crisis Orchestration System</div>
    <div class="hdr-sub">Multi-Occupancy Buildings · Detection → Decision → Assignment → Verification · Firefighter Integration</div>
  </div>
  <div class="team-badge-header" style="position:absolute; right:150px; top:50%; transform:translateY(-50%); font-size:10px; color:#64748b;">
    🎓 Built by Team CrisisAI • Pragati Engineering College
  </div>
  <div style="display:flex;gap:8px;align-items:center;position:relative;z-index:2;">
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

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🗺️  Live Map", "🧠  AI Reasoning", "🎯  Planner", "✅  Verification", "🚒  Firefighter", "📱 Mobile Responder"
])

# ══ TAB 1 — LIVE MAP ══════════════════════════════════════════════════════════
with tab1:
    # ── AI DECISION ENGINE — LIVE REASONING PANEL ─────────────────────────────
    live_bullets = build_live_reasoning(
        decs, asns, sim, st.session_state.plan,
        prev_decisions=st.session_state.get("prev_decisions", {})
    ) if decs else [
        "🤖 Initialize the system and run a tick to see live AI reasoning.",
        "📊 Fire spread prediction, patient risk scoring, and staff routing will appear here.",
    ]
    bullets_html = "".join(
        f'<div style="display:flex;gap:10px;margin-bottom:7px;align-items:flex-start">'
        f'<span style="color:#22c55e;font-size:16px;line-height:1.3;flex-shrink:0">•</span>'
        f'<span style="font-size:13px;color:#86efac;line-height:1.8;font-style:italic">{b}</span>'
        f'</div>'
        for b in live_bullets
    )
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0a1e0a,#051510);border:1px solid #22c55e40;
                border-radius:12px;padding:16px 20px;margin-bottom:16px">
      <div style="font-size:14px;font-weight:700;color:#22c55e;margin-bottom:12px;
                  letter-spacing:.5px;display:flex;align-items:center;gap:10px">
        🧠 AI DECISION ENGINE — LIVE REASONING
        <span style="background:#22c55e;color:#000;font-size:9px;font-weight:800;
                     padding:2px 9px;border-radius:20px;letter-spacing:1px;
                     animation:pulse 1.6s infinite">TICK {tick_val:03d}</span>
      </div>
      {bullets_html}
    </div>""", unsafe_allow_html=True)

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

        # ── CHANGE 3a: Fire spread direction arrow ─────────────────────────────
        ff_brief = st.session_state.get("ff_briefing")
        if ff_brief and ff_brief.get("fire_spread_direction"):
            raw_dir = ff_brief["fire_spread_direction"]
        elif sim.fire and len(sim.fire) >= 4:
            _fc = list(sim.fire)
            _cx = sum(x for x,y,*_ in _fc)/len(_fc); _cy = sum(y for x,y,*_ in _fc)/len(_fc)
            _rc = _fc[-max(4,len(_fc)//4):]
            _rcx = sum(x for x,y,*_ in _rc)/len(_rc); _rcy = sum(y for x,y,*_ in _rc)/len(_rc)
            _h = "East" if _rcx>_cx+0.3 else ("West" if _rcx<_cx-0.3 else "")
            _v = "North" if _rcy<_cy-0.3 else ("South" if _rcy>_cy+0.3 else "")
            raw_dir = (_v+_h).strip() or "Radial"
        else:
            raw_dir = "Radial"
        _arrows = {"North":"↑","South":"↓","East":"→","West":"←",
                   "Northeast":"↗","NorthEast":"↗","Southeast":"↘","SouthEast":"↘",
                   "Southwest":"↙","SouthWest":"↙","Northwest":"↖","NorthWest":"↖",
                   "Radial":"⭕","RADIAL":"⭕"}
        _arrow = _arrows.get(raw_dir, "⭕")
        if sim.fire:
            st.markdown(
                f'<div style="background:#1a0a0a;border:1px solid #ef444450;border-radius:8px;'
                f'padding:8px 14px;margin-bottom:8px;display:flex;align-items:center;gap:10px">'
                f'<span style="font-size:20px">{_arrow}</span>'
                f'<span style="font-size:15px;font-weight:700;color:#ef4444">'
                f'🔥 Fire spreading {_arrow} <b>{raw_dir.upper()}</b></span>'
                f'</div>', unsafe_allow_html=True)

        # ── CHANGE 1b: Predicted fire count banner ─────────────────────────────
        if predicted:
            st.markdown(
                f'<div style="background:linear-gradient(90deg,#2d2000,#1a1400);'
                f'border:1px solid #eab30870;border-radius:8px;padding:8px 14px;'
                f'margin-bottom:8px;display:flex;align-items:center;gap:10px">'
                f'<span style="font-size:16px">⚠️</span>'
                f'<span style="font-size:13px;font-weight:700;color:#eab308">'
                f'PREDICTED FIRE ZONES (NEXT 3 TICKS): '
                f'<span style="font-size:18px;font-family:\'JetBrains Mono\'">{len(predicted)}</span> cells'
                f'</span></div>', unsafe_allow_html=True)

        # ── CHANGE 2b: Build priority_map for grid badges ──────────────────────
        priority_map = {d["patient_id"]: d["explanation"]["priority_level"] for d in decs} if decs else {}

        st.markdown(render_grid(sim, floor=vfloor, predicted_fire=predicted,
                                fire_new_cells=fire_new, priority_map=priority_map),
                    unsafe_allow_html=True)
        if updated:
            st.session_state.tick_updated = False

    with c2:
        st.markdown('<div class="slabel">Priority Decisions</div>', unsafe_allow_html=True)
        if decs:
            st.markdown(render_priorities(decs, sim.patients, prev_decisions=st.session_state.get("prev_decisions", {})), unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#334155;font-size:13px;padding:10px">Run a tick to see priorities.</div>', unsafe_allow_html=True)
        st.markdown('<div class="slabel" style="margin-top:12px">Staff Assignments</div>', unsafe_allow_html=True)
        st.markdown(render_assignments(asns, prev_assignments=st.session_state.get("prev_assignments", {})), unsafe_allow_html=True)

    # ── CRISIS TIMELINE (TICKER) ──────────────────────────────────────────────
    st.markdown("""
    <style>
    .ticker-wrap { width: 100%; overflow: hidden; background: #0a0f1e; border: 1px solid #1e2a40; border-radius: 8px; padding: 10px; margin-top: 16px; display: flex; align-items: center; box-shadow: inset 0 2px 4px rgba(0,0,0,0.5); }
    .ticker-label { font-size: 11px; font-weight: 900; color: #64748b; letter-spacing: 1px; margin-right: 16px; flex-shrink: 0; padding-right: 16px; border-right: 1px solid #1e2a40; }
    .ticker-content { display: flex; gap: 20px; overflow-x: auto; white-space: nowrap; scroll-behavior: smooth; padding-bottom: 4px; }
    .ticker-content::-webkit-scrollbar { height: 4px; }
    .ticker-content::-webkit-scrollbar-thumb { background: #1e2a40; border-radius: 4px; }
    .ticker-item { display: inline-flex; align-items: center; gap: 8px; font-size: 12px; padding: 4px 12px; border-radius: 20px; background: #111827; border: 1px solid #1f2937; animation: slideInRight 0.5s ease-out forwards; }
    @keyframes slideInRight { from { opacity: 0; transform: translateX(20px); } to { opacity: 1; transform: translateX(0); } }
    </style>
    <div class="ticker-wrap">
      <div class="ticker-label">⏱️ CRISIS TICKER</div>
      <div class="ticker-content" id="ticker-box">
    """, unsafe_allow_html=True)

    timeline_events = st.session_state.get("timeline", [])
    if not timeline_events:
        st.markdown('<div style="color:#475569;font-size:12px;font-style:italic;padding:4px;">Awaiting crisis events...</div>', unsafe_allow_html=True)
    else:
        events_html = ""
        # Display latest events horizontally
        for ev in reversed(timeline_events[-20:]):
            events_html += f"""
            <div class="ticker-item">
              <span style="color:#94a3b8;font-family:'JetBrains Mono';font-size:10px;font-weight:bold;">T{ev['tick']:03d}</span>
              <span>{ev['icon']}</span>
              <span style="color:{ev['color']}">{ev['msg']}</span>
            </div>
            """
        st.markdown(events_html, unsafe_allow_html=True)
    
    st.markdown("""
      </div>
    </div>
    <script>
      // Auto-scroll ticker to the latest (left side since we reversed it)
      const tbox = document.getElementById("ticker-box");
      if(tbox) tbox.scrollLeft = 0;
    </script>
    """, unsafe_allow_html=True)

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
                  <div style="margin-top:16px; display:flex; align-items:center; gap:16px;">
                    <div style="position:relative; width:80px; height:80px; border-radius:50%; background:conic-gradient({sc_c} {p['survival_probability']}%, #1e2a40 0); display:flex; align-items:center; justify-content:center; box-shadow:0 0 15px {sc_c}40;">
                      <div style="width:66px; height:66px; background:#0f1629; border-radius:50%; display:flex; flex-direction:column; align-items:center; justify-content:center;">
                        <span style="font-size:18px; font-weight:900; color:{sc_c}; font-family:'JetBrains Mono'">{p['survival_probability']}%</span>
                      </div>
                    </div>
                    <div>
                      <div style="font-size:10px; color:#94a3b8; font-weight:800; letter-spacing:1px;">SURVIVAL<br>PROBABILITY</div>
                    </div>
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

# ══ TAB 6 — MOBILE RESPONDER VIEW ════════════════════════════════════════════
with tab6:
    st.markdown('<div class="slabel">Touch-Optimized Emergency Interface</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#0a1020;border:1px solid #1e2a40;border-radius:10px;
                padding:13px 18px;font-size:13px;color:#64748b;margin-bottom:14px;line-height:1.7">
      This view simulates the <b style="color:#22c55e">CrisisAI Responder App</b> used by on-the-ground staff and firefighters.
      It focuses purely on actionable tasks, big touch targets, and critical warnings.
    </div>""", unsafe_allow_html=True)

    c_mob1, c_mob2, c_mob3 = st.columns([1, 2, 1])
    with c_mob2:
        st.markdown(f"""
        <div style="width: 100%; max-width: 380px; margin: 0 auto; border: 8px solid #1e2a40; border-radius: 36px; padding: 20px 16px; background: #050810; box-shadow: 0 20px 40px rgba(0,0,0,0.5); position: relative;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 20px; border-bottom: 1px solid #1e2a40; padding-bottom: 12px;">
            <div style="font-size:16px; font-weight:900; color:#ef4444;">🚨 CrisisAI</div>
            <div style="font-size:12px; color:#cbd5e1; font-family:'JetBrains Mono';">TICK {tick_val:03d}</div>
          </div>
        """, unsafe_allow_html=True)

        if not asns.get("assignments"):
            st.markdown("""
            <div style="text-align:center; padding: 40px 10px; color:#475569;">
              <div style="font-size:48px; margin-bottom:16px;">📱</div>
              <div style="font-size:16px; font-weight:700;">No Active Assignments</div>
              <div style="font-size:12px; margin-top:8px;">Awaiting AI dispatch...</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-size:12px; font-weight:800; color:#94a3b8; letter-spacing:1px; margin-bottom:12px;">YOUR CURRENT TASKS</div>', unsafe_allow_html=True)
            for a in asns["assignments"][:2]:
                pid = a["patient_id"]
                room = a["target_room"]
                is_saved = any(p.id == pid and getattr(p, "evacuated", False) for p in (sim.patients if sim else []))
                
                if is_saved:
                    st.markdown(f"""
                    <div style="background:#0a1e0a; border: 1px solid #22c55e50; border-left: 4px solid #22c55e; border-radius: 12px; padding: 16px; margin-bottom: 12px;">
                      <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div style="font-size:16px; font-weight:800; color:#f1f5f9;">Evacuate Patient {pid}</div>
                        <div style="background:#22c55e; color:#000; font-size:10px; font-weight:800; padding:2px 8px; border-radius:12px;">SAVED</div>
                      </div>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background:#0f1629; border: 1px solid #3b82f650; border-left: 4px solid #3b82f6; border-radius: 12px; padding: 16px; margin-bottom: 8px;">
                      <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px;">
                        <div style="font-size:16px; font-weight:800; color:#f1f5f9;">Evacuate Patient {pid}</div>
                        <div style="background:#3b82f6; color:#fff; font-size:10px; font-weight:800; padding:2px 8px; border-radius:12px;">ACTIVE</div>
                      </div>
                      <div style="font-size:13px; color:#94a3b8; margin-bottom:12px;">
                        📍 Location: Room {room}<br>
                        ⚠️ Priority: HIGH
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    bcol1, bcol2 = st.columns(2)
                    with bcol1:
                        if st.button(f"✅ DONE", key=f"done_{pid}_{tick_val}", use_container_width=True, type="primary"):
                            for p in sim.patients:
                                if p.id == pid:
                                    p.evacuated = True
                            if _verif and pid in _verif.tasks:
                                _verif.tasks[pid]["status"] = "completed"
                                _verif.tasks[pid]["completed_tick"] = sim.tick
                            st.session_state.timeline.append({"tick": sim.tick, "icon": "✅", "color": "#22c55e", "msg": f"Mobile App: Patient {pid} marked safe."})
                            st.rerun()
                    with bcol2:
                        if st.button(f"🆘 HELP", key=f"help_{pid}_{tick_val}", use_container_width=True):
                            if _verif and pid in _verif.tasks:
                                _verif.tasks[pid]["status"] = "failed"
                                _verif.tasks[pid]["reason"] = "Responder requested help"
                            st.session_state.timeline.append({"tick": sim.tick, "icon": "🆘", "color": "#ef4444", "msg": f"Mobile App: SOS received for Patient {pid}."})
                            st.rerun()
                    st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)

            if sim and sim.fire:
                st.markdown("""
                <div style="background:#3b0a0a; border: 1px solid #ef444450; border-radius: 12px; padding: 14px; margin-top: 16px; animation: pulse 2s infinite;">
                  <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
                    <span style="font-size:20px;">🔥</span>
                    <span style="font-size:14px; font-weight:800; color:#ef4444;">HAZARD WARNING</span>
                  </div>
                  <div style="font-size:12px; color:#fca5a5; line-height:1.4;">
                    Fire spreading in building. Maintain safe clearance.
                  </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("""
          <div style="display:flex; justify-content:space-around; padding-top: 20px; margin-top: 20px; border-top: 1px solid #1e2a40;">
            <div style="text-align:center; color:#3b82f6;"><div style="font-size:20px;">📋</div><div style="font-size:9px; font-weight:700; margin-top:4px;">TASKS</div></div>
            <div style="text-align:center; color:#64748b;"><div style="font-size:20px;">🗺️</div><div style="font-size:9px; font-weight:700; margin-top:4px;">MAP</div></div>
            <div style="text-align:center; color:#64748b;"><div style="font-size:20px;">💬</div><div style="font-size:9px; font-weight:700; margin-top:4px;">COMMS</div></div>
          </div>
        </div>
        """, unsafe_allow_html=True)
