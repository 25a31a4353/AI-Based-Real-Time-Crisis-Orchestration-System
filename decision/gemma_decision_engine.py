"""
Gemma 4-Powered Decision Layer for CrisisAI
============================================
Uses Google's Gemma 4 model (via google-genai SDK) to:
  1. Analyse simulated sensor data (temperature + smoke) to predict fire spread direction.
  2. Return a plain-language AI reasoning string that the dashboard can display.

The numeric Priority Score formula is still computed deterministically:
    P = w1*Risk + w2*Immobility + w3*Urgency - w4*NearbyHelp

Gemma only adds qualitative reasoning on TOP of that score, so the system
remains fully functional even when offline / when the API is unavailable.
"""

import os
import json
import threading

# ── Try to import the Google GenAI SDK ───────────────────────────────────────
try:
    from google import genai
    from google.genai import types
    _GENAI_AVAILABLE = True
except ImportError:
    _GENAI_AVAILABLE = False


# ── Gemma 4 client (lazy-initialised) ────────────────────────────────────────
_client = None

def _get_client():
    global _client
    if _client is not None:
        return _client
    if not _GENAI_AVAILABLE:
        return None
    api_key = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("GOOGLE_API_KEY", "")
    if not api_key:
        return None
    _client = genai.Client(api_key=api_key)
    return _client


# ── Gemma 4 Fire-Spread Predictor ─────────────────────────────────────────────
def predict_fire_direction_gemma(simulation) -> str:
    """
    Sends a compact sensor snapshot to Gemma 4 and asks it to predict the
    dominant fire-spread direction + brief reasoning.

    Falls back to a deterministic heuristic if the API is unavailable.
    Returns a plain-text string (1-3 sentences).
    """
    client = _get_client()
    if client is None:
        return _heuristic_direction(simulation)

    # Build a compact sensor summary (≤ 400 tokens)
    fire_cells = simulation.fire
    if not fire_cells:
        return "No active fire detected."

    sev_summary = {
        str(pos): simulation.fire_severity.get(pos, 1)
        for pos in fire_cells[:12]          # cap to 12 cells
    }

    # Average temperature in the 4 quadrants around the centroid
    cx = sum(x for x, y, *_ in fire_cells) / len(fire_cells)
    cy = sum(y for x, y, *_ in fire_cells) / len(fire_cells)
    W, H = simulation.building.width, simulation.building.height

    def avg_temp(x_range, y_range):
        vals = [simulation.temperature_map[y][x]
                for x in x_range for y in y_range
                if 0 <= x < W and 0 <= y < H]
        return round(sum(vals) / len(vals), 1) if vals else 20.0

    int_cx, int_cy = int(cx), int(cy)
    quadrant_temps = {
        "North": avg_temp(range(max(0, int_cx-2), min(W, int_cx+3)),
                          range(max(0, int_cy-4), int_cy+1)),
        "South": avg_temp(range(max(0, int_cx-2), min(W, int_cx+3)),
                          range(int_cy, min(H, int_cy+4))),
        "East":  avg_temp(range(int_cx, min(W, int_cx+4)),
                          range(max(0, int_cy-2), min(H, int_cy+3))),
        "West":  avg_temp(range(max(0, int_cx-4), int_cx+1),
                          range(max(0, int_cy-2), min(H, int_cy+3))),
    }

    # Peak smoke values by quadrant
    def max_smoke(x_range, y_range):
        vals = [simulation.smoke_map[y][x]
                for x in x_range for y in y_range
                if 0 <= x < W and 0 <= y < H]
        return round(max(vals), 2) if vals else 0.0

    quadrant_smoke = {
        "North": max_smoke(range(max(0, int_cx-2), min(W, int_cx+3)),
                           range(max(0, int_cy-4), int_cy+1)),
        "South": max_smoke(range(max(0, int_cx-2), min(W, int_cx+3)),
                           range(int_cy, min(H, int_cy+4))),
        "East":  max_smoke(range(int_cx, min(W, int_cx+4)),
                           range(max(0, int_cy-2), min(H, int_cy+3))),
        "West":  max_smoke(range(max(0, int_cx-4), int_cx+1),
                           range(max(0, int_cy-2), min(H, int_cy+3))),
    }

    sensor_payload = {
        "tick": simulation.tick,
        "fire_cell_count": len(fire_cells),
        "fire_centroid": {"x": round(cx, 1), "y": round(cy, 1)},
        "severity_sample": sev_summary,
        "quadrant_temperatures_C": quadrant_temps,
        "quadrant_peak_smoke_0_to_1": quadrant_smoke,
        "building_size": f"{W}x{H}",
    }

    prompt = f"""You are an AI fire-behaviour analyst embedded in a hospital crisis-management system.
Below is real-time sensor data from Tick {simulation.tick} of the simulation.

SENSOR DATA:
{json.dumps(sensor_payload, indent=2)}

Analyse the temperature and smoke gradients across the four quadrants.
Answer in exactly 2 sentences:
1. State the dominant fire-spread direction (North/South/East/West/Radial) and why.
2. Name one building zone at immediate risk and advise the crisis coordinator.

Be concise and authoritative. Do NOT include disclaimers."""

    try:
        result = [None]
        exc    = [None]

        def _call():
            try:
                resp = client.models.generate_content(
                    model="gemma-3-27b-it",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.3,
                        max_output_tokens=150,
                    ),
                )
                result[0] = resp.text.strip()
            except Exception as e:
                exc[0] = e

        t = threading.Thread(target=_call, daemon=True)
        t.start()
        t.join(timeout=4.0)   # 4-second hard cap — UI never freezes

        if t.is_alive() or exc[0]:
            reason = str(exc[0]) if exc[0] else "timeout"
            return f"[Gemma {reason}] " + _heuristic_direction(simulation)
        return result[0]
    except Exception as exc:
        return f"[Gemma unavailable: {exc}] " + _heuristic_direction(simulation)


def _heuristic_direction(simulation) -> str:
    """Deterministic fallback — uses temperature gradients to find spread direction."""
    fire_cells = simulation.fire
    if not fire_cells:
        return "No active fire cells."

    cx = sum(x for x, y, *_ in fire_cells) / len(fire_cells)
    cy = sum(y for x, y, *_ in fire_cells) / len(fire_cells)

    # Use newest fire cells (last 4) to determine direction
    recent = fire_cells[-min(4, len(fire_cells)):]
    ncx = sum(x for x, y, *_ in recent) / len(recent)
    ncy = sum(y for x, y, *_ in recent) / len(recent)

    hdir = "East" if ncx > cx + 0.3 else ("West" if ncx < cx - 0.3 else "")
    vdir = "South" if ncy > cy + 0.3 else ("North" if ncy < cy - 0.3 else "")
    direction = f"{vdir}-{hdir}".strip("-") or "Radial"

    return (
        f"Fire is spreading {direction} based on thermal gradient analysis. "
        f"Fire centroid is at ({round(cx,1)}, {round(cy,1)}) — "
        f"zones in this direction require immediate evacuation priority."
    )


# ── Main Decision Engine (Gemma-enhanced) ────────────────────────────────────
def run_decision_engine_gemma(simulation, weights=None):
    """
    Gemma 4-enhanced Decision Engine.

    Returns the same structure as run_decision_engine() from decision_engine.py,
    PLUS:
      - "ai_fire_direction"  : Gemma's fire-spread prediction string
      - "ai_reasoning"       : per-patient AI commentary (generated once per call)

    Priority Score: P = w1*Risk + w2*Immobility + w3*Urgency - w4*NearbyHelp
    ICU patients (immobile) always receive the highest immobility weight (1.5 * 45).
    """
    if weights is None:
        weights = {"risk": 1.2, "immobility": 1.5, "urgency": 1.0, "nearby_help": 0.8}

    w1, w2, w3, w4 = (weights["risk"], weights["immobility"],
                      weights["urgency"], weights["nearby_help"])

    # ── Gemma fire direction prediction ──────────────────
    ai_fire_direction = predict_fire_direction_gemma(simulation)

    predicted_fire_raw = simulation.predict_fire_spread(ticks_ahead=3)
    predicted_fire = [(x,y) for x,y,f in predicted_fire_raw]
    predicted_set  = set(predicted_fire)

    decisions = []

    for p in simulation.patients:
        if p.evacuated:
            continue

        # ── Factor 1: RISK ────────────────────────────────────────────────────
        risk = 0.0
        for (fx, fy, f, *_) in simulation.fire:
            dist = abs(p.x - fx) + abs(p.y - fy)
            sev  = simulation.fire_severity.get((fx, fy, f), 1)
            if dist == 0:
                risk += 55 * sev
            elif dist <= 2:
                risk += (28 / dist) * sev
            elif dist <= 5:
                risk += (12 / dist) * sev

        for (fx, fy) in predicted_set:
            dist = abs(p.x - fx) + abs(p.y - fy)
            if dist <= 3:
                risk += 8 / max(dist, 1)

        fl = min(getattr(p, 'floor', 0), simulation.building.floors - 1)
        temp  = simulation.temperature_map[fl][p.y][p.x]
        smoke = simulation.smoke_map[fl][p.y][p.x]
        if temp > 55:
            risk += (temp - 55) * 0.6
        risk += smoke * 18

        # ── Factor 2: IMMOBILITY ─────────────────────────────────────────────
        # ICU patients are ALWAYS prioritised highest via the immobility score.
        immobility = 0.0
        if not p.movable:
            immobility = 45          # ICU — cannot self-evacuate under any circumstance
        elif getattr(p, "condition", "stable") == "critical":
            immobility = 20          # mobile but needs assistance

        # ── Factor 3: URGENCY ────────────────────────────────────────────────
        min_fire_dist = min(
            (abs(p.x - fx) + abs(p.y - fy) for fx, fy, *_ in simulation.fire),
            default=999,
        )
        if   min_fire_dist == 0: urgency = 60
        elif min_fire_dist == 1: urgency = 45
        elif min_fire_dist == 2: urgency = 30
        elif min_fire_dist <= 4: urgency = 18
        elif min_fire_dist <= 6: urgency = 8
        else:                    urgency = 0

        # ── Factor 4: NEARBY HELP ────────────────────────────────────────────
        nearby_help = 0.0
        for s in simulation.staff:
            d = abs(p.x - s.x) + abs(p.y - s.y)
            if d <= 2: nearby_help += 18
            elif d <= 4: nearby_help += 8

        # ── FINAL PRIORITY ────────────────────────────────────────────────────
        score = (w1*risk + w2*immobility + w3*urgency) - (w4*nearby_help)
        score = max(0.0, round(score, 1))

        if   score > 80: level = "critical"
        elif score > 45: level = "high"
        elif score > 20: level = "medium"
        else:            level = "low"

        decisions.append({
            "patient_id":  p.id,
            "priority":    score,
            "explanation": {
                "priority_level":   level,
                "risk_score":       round(w1 * risk, 1),
                "immobility_score": round(w2 * immobility, 1),
                "urgency_score":    round(w3 * urgency, 1),
                "nearby_help":      round(w4 * nearby_help, 1),
                "temperature":      round(temp, 1),
                "smoke_level":      round(smoke, 2),
                "min_fire_dist":    min_fire_dist,
            },
            "is_icu":                not p.movable,
            "predicted_fire_nearby": any(
                abs(p.x - fx) + abs(p.y - fy) <= 3 for fx, fy in predicted_set
            ),
        })

    decisions.sort(key=lambda x: x["priority"], reverse=True)

    return {
        "decisions":          decisions,
        "ai_fire_direction":  ai_fire_direction,
    }
