"""
CrisisAI — FastAPI Backend
==========================
Endpoints:
  GET  /health                   → health check
  POST /api/tick                 → advance simulation one tick
  GET  /api/state                → full simulation state snapshot
  GET  /api/safe-routes          → safe evacuation routes (mobile UI)
  GET  /api/hazard-alerts        → active hazard zones (mobile UI)
  POST /api/ai/fire-direction    → Vertex AI Gemma 4 fire prediction
  GET  /api/dashboard            → combined control dashboard payload

Cloud Run: listens on PORT env var (default 8080).
"""

import os
import json
import asyncio
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ── local engine imports ──────────────────────────────────────────────────────
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from simulation.simulation_engine   import Simulation, Building, Patient, Staff
from decision.gemma_decision_engine import run_decision_engine_gemma
from assignment.assignment_engine   import run_assignment
from verification.verification_engine import VerificationEngine
from planner.simulation_planner     import run_planner
from firefighter.firefighter_module import get_firefighter_briefing
from api.vertex_client              import get_fire_direction_vertex

# ── App lifecycle ─────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    _reset_simulation()
    yield

app = FastAPI(
    title="CrisisAI Control API",
    description="AI-Based Real-Time Crisis Orchestration System — Cloud Run Backend",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory simulation state (single instance for prototype) ────────────────
_sim: Optional[Simulation] = None
_verifier: Optional[VerificationEngine] = None
_last_decisions = []
_last_assignments = {"assignments": []}
_last_plan = None
_last_ff = None
_last_verification = {}
_ai_fire_direction = ""


def _reset_simulation():
    global _sim, _verifier, _last_decisions, _last_assignments
    global _last_plan, _last_ff, _last_verification, _ai_fire_direction

    building = Building(10, 10)
    patients = [
        Patient(0, 9, 2, movable=True,  condition="stable"),
        Patient(1, 2, 7, movable=False, condition="critical"),   # ICU
        Patient(2, 1, 7, movable=True,  condition="stable"),
        Patient(3, 8, 2, movable=False, condition="critical"),   # ICU
        Patient(4, 6, 2, movable=False, condition="stable"),     # ICU
    ]
    staff = [
        Staff(0, 2, 4, trained=True,  role="medic"),
        Staff(1, 5, 5, trained=False, role="nurse"),
        Staff(2, 7, 5, trained=True,  role="medic"),
    ]
    _sim = Simulation(building, patients, staff)
    _verifier = VerificationEngine(deadline_ticks=3)
    _last_decisions = []
    _last_assignments = {"assignments": []}
    _last_plan = None
    _last_ff = None
    _last_verification = {}
    _ai_fire_direction = ""


def _build_state_snapshot():
    """Serialise current simulation state to a JSON-safe dict."""
    return {
        "tick":        _sim.tick,
        "fire_cells":  len(_sim.fire),
        "fire":        [{"x": x, "y": y, "severity": _sim.fire_severity.get((x, y), 1)}
                        for x, y in _sim.fire],
        "patients": [
            {
                "id":        p.id,
                "x":         p.x,
                "y":         p.y,
                "movable":   p.movable,
                "condition": p.condition,
                "evacuated": p.evacuated,
                "status":    p.status,
                "path":      p.path,
            }
            for p in _sim.patients
        ],
        "staff": [
            {"id": s.id, "x": s.x, "y": s.y, "role": s.role, "trained": s.trained, "path": s.path}
            for s in _sim.staff
        ],
        "firefighters": [
            {"id": f.id, "x": f.x, "y": f.y, "zone": f.assigned_zone}
            for f in _sim.firefighters
        ],
        "exits": _sim.building.exits,
        "rescued_count": _sim.rescued_count,
        "failed_count": _sim.failed_count,
        "survival_rate": _sim.get_survival_rate(),
    }


# ── Request / Response models ─────────────────────────────────────────────────
class FireDirectionRequest(BaseModel):
    tick: int
    fire_cells: list
    temperature_snapshot: dict
    smoke_snapshot: dict


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "service": "CrisisAI Control API", "tick": _sim.tick if _sim else -1}


@app.post("/api/reset", tags=["Simulation"])
def reset():
    _reset_simulation()
    return {"message": "Simulation reset.", "tick": 0}


@app.post("/api/tick", tags=["Simulation"])
async def advance_tick():
    """Advance simulation by one tick and run all AI engines."""
    global _last_decisions, _last_assignments, _last_plan
    global _last_ff, _last_verification, _ai_fire_direction

    if _sim is None:
        raise HTTPException(500, "Simulation not initialised.")

    _sim.update_fire()

    # Gemma 4 / Vertex AI decision engine
    result        = run_decision_engine_gemma(_sim)
    _last_decisions   = result["decisions"]
    _ai_fire_direction = result["ai_fire_direction"]

    _last_assignments = run_assignment(_sim, _last_decisions)

    # Update Staff Paths from new assignments
    for assignment in _last_assignments["assignments"]:
        s = next((s for s in _sim.staff if s.id == assignment["staff_id"]), None)
        p = next((p for p in _sim.patients if p.id == assignment["patient_id"]), None)
        if s and p:
            s.path = p.path

    # Coordinate Firefighters
    from main import coordinate_firefighters
    coordinate_firefighters(_sim, _last_assignments["unreachable_patients"])

    _verifier.register_assignments(_last_assignments, _sim.tick)
    _last_verification = _verifier.verify_tick(_sim, _sim.tick)
    _last_plan        = run_planner(_sim)
    _last_ff          = get_firefighter_briefing(_sim)

    return {
        "tick":             _sim.tick,
        "fire_cells":       len(_sim.fire),
        "assignments":      len(_last_assignments["assignments"]),
        "unreachable":      len(_last_assignments["unreachable_patients"]),
        "ai_fire_direction": _ai_fire_direction,
        "verification":     _verifier.summary(),
        "success_stats": {
            "rescued": _sim.rescued_count,
            "failed": _sim.failed_count,
            "survival_rate": _sim.get_survival_rate()
        }
    }


@app.get("/api/state", tags=["Simulation"])
def get_state():
    if _sim is None:
        raise HTTPException(500, "Simulation not initialised.")
    return _build_state_snapshot()


# ─────────────────────────────────────────────────────────────────────────────
# MOBILE UI — SAFE ROUTES
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/safe-routes", tags=["Mobile UI"])
def safe_routes():
    """
    Returns a list of safe evacuation routes for mobile client rendering.
    Each route has: staff_id, patient_id, waypoints[], status, risk_level.
    """
    if _sim is None:
        raise HTTPException(500, "Simulation not initialised.")

    routes = []
    fire_set = set(_sim.fire)

    for a in _last_assignments.get("assignments", []):
        staff   = next((s for s in _sim.staff   if s.id == a["staff_id"]),   None)
        patient = next((p for p in _sim.patients if p.id == a["patient_id"]), None)
        if not staff or not patient:
            continue

        # Build a simple straight-line waypoint list (5 steps)
        waypoints = []
        steps = 5
        for i in range(steps + 1):
            t  = i / steps
            wx = round(staff.x + t * (patient.x - staff.x))
            wy = round(staff.y + t * (patient.y - staff.y))
            on_fire = (wx, wy) in fire_set
            smoke   = round(_sim.smoke_map[wy][wx], 2)
            waypoints.append({
                "x":       wx,
                "y":       wy,
                "on_fire": on_fire,
                "smoke":   smoke,
            })

        bd = a.get("cost_breakdown", {})
        path_risk = bd.get("path_risk", 0)
        if path_risk > 25:
            risk_level = "HIGH"
            warning    = "Fire on route — use alternate corridor"
        elif path_risk > 8:
            risk_level = "MEDIUM"
            warning    = "Smoke on path — proceed with mask"
        else:
            risk_level = "LOW"
            warning    = "Route clear"

        routes.append({
            "route_id":    f"R{a['staff_id']}-P{a['patient_id']}",
            "staff_id":    a["staff_id"],
            "patient_id":  a["patient_id"],
            "target_room": a["target_room"],
            "waypoints":   waypoints,
            "risk_level":  risk_level,
            "warning":     warning,
            "cost":        bd.get("total_cost", "?"),
        })

    return {
        "tick":   _sim.tick,
        "routes": routes,
        "count":  len(routes),
    }


# ─────────────────────────────────────────────────────────────────────────────
# MOBILE UI — HAZARD ALERTS
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/hazard-alerts", tags=["Mobile UI"])
def hazard_alerts():
    """
    Returns active hazard alerts for mobile client push notifications.
    Includes: fire zones, predicted spread, smoke zones, critical patients.
    """
    if _sim is None:
        raise HTTPException(500, "Simulation not initialised.")

    alerts = []

    # Active fire cells (severity ≥ 3 = CRITICAL)
    for (x, y), sev in _sim.fire_severity.items():
        level = "CRITICAL" if sev >= 3 else "WARNING"
        alerts.append({
            "type":     "FIRE",
            "level":    level,
            "location": {"x": x, "y": y},
            "severity": sev,
            "message":  f"Active fire at ({x},{y}) — severity {sev}/4",
        })

    # Predicted spread zones
    predicted = _sim.predict_fire_spread(ticks_ahead=2)
    for (x, y) in predicted[:10]:   # cap to 10 to avoid payload bloat
        alerts.append({
            "type":     "PREDICTED_FIRE",
            "level":    "WARNING",
            "location": {"x": x, "y": y},
            "severity": 0,
            "message":  f"Fire predicted at ({x},{y}) within 2 ticks",
        })

    # Heavy smoke zones
    W, H = _sim.building.width, _sim.building.height
    for y in range(H):
        for x in range(W):
            s = _sim.smoke_map[y][x]
            if s > 0.7:
                alerts.append({
                    "type":     "HEAVY_SMOKE",
                    "level":    "WARNING",
                    "location": {"x": x, "y": y},
                    "severity": round(s, 2),
                    "message":  f"Heavy smoke at ({x},{y}) — level {round(s,2)}",
                })

    # Critical ICU patients not yet evacuated
    for p in _sim.patients:
        if not p.movable and not p.evacuated:
            dist = min(
                (abs(p.x - fx) + abs(p.y - fy) for fx, fy in _sim.fire),
                default=999,
            )
            if dist <= 4:
                alerts.append({
                    "type":     "CRITICAL_PATIENT",
                    "level":    "CRITICAL",
                    "location": {"x": p.x, "y": p.y},
                    "severity": 4,
                    "message":  f"ICU Patient {p.id} at ({p.x},{p.y}) — fire {dist} cells away",
                })

    # Reassignment failures
    for r in _last_verification.get("reassign_needed", []):
        alerts.append({
            "type":     "TASK_FAILED",
            "level":    "CRITICAL",
            "location": {},
            "severity": 4,
            "message":  f"Patient {r['patient_id']} rescue FAILED — {r['reason']}",
        })

    # Sort: CRITICAL first
    order = {"CRITICAL": 0, "WARNING": 1, "INFO": 2}
    alerts.sort(key=lambda a: order.get(a["level"], 2))

    return {
        "tick":   _sim.tick,
        "alerts": alerts,
        "count":  len(alerts),
        "ai_fire_direction": _ai_fire_direction,
    }


# ─────────────────────────────────────────────────────────────────────────────
# CONTROL DASHBOARD — combined payload
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/dashboard", tags=["Dashboard"])
def dashboard():
    """
    Combined control dashboard payload — all data a React/mobile dashboard needs.
    """
    if _sim is None:
        raise HTTPException(500, "Simulation not initialised.")

    vcounts = _verifier.summary() if _verifier else {}

    return {
        "tick":              _sim.tick,
        "fire_cells":        len(_sim.fire),
        "ai_fire_direction": _ai_fire_direction,
        "stats": {
            "fire_cells":  len(_sim.fire),
            "assignments": len(_last_assignments.get("assignments", [])),
            "completed":   vcounts.get("completed", 0) + vcounts.get("likely_complete", 0),
            "failed":      vcounts.get("failed", 0),
            "top_patient": _last_decisions[0]["patient_id"] if _last_decisions else None,
            "top_score":   _last_decisions[0]["priority"]   if _last_decisions else 0,
        },
        "decisions":    _last_decisions,
        "assignments":  _last_assignments.get("assignments", []),
        "plan":         _last_plan,
        "verification": _last_verification,
        "ff_briefing":  _last_ff,
        "state":        _build_state_snapshot(),
    }


# ─────────────────────────────────────────────────────────────────────────────
# VERTEX AI — Fire direction endpoint
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/api/ai/fire-direction", tags=["Vertex AI"])
async def fire_direction_ai(req: FireDirectionRequest):
    """
    Calls Vertex AI (Gemma 4 on google-genai) to predict fire spread direction
    from raw sensor data. Use this endpoint from your mobile client.
    """
    try:
        result = await asyncio.to_thread(get_fire_direction_vertex, req.dict())
        return {"prediction": result, "tick": req.tick}
    except Exception as exc:
        raise HTTPException(500, f"Vertex AI call failed: {exc}")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("api.main:app", host="0.0.0.0", port=port, reload=False)
