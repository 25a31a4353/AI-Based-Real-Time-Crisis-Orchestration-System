"""
Vertex AI client for CrisisAI
==============================
Calls Gemma 4 (gemma-3-27b-it) via google-genai SDK, authenticated with
Application Default Credentials (ADC) on Cloud Run.

On Cloud Run, no API key is needed — ADC uses the service account automatically.
Locally, set GOOGLE_APPLICATION_CREDENTIALS or GEMINI_API_KEY.
"""

import os
import json
from typing import Union

try:
    from google import genai
    from google.genai import types
    _SDK_AVAILABLE = True
except ImportError:
    _SDK_AVAILABLE = False

# ── Client factory ────────────────────────────────────────────────────────────
_client = None

def _get_client():
    global _client
    if _client:
        return _client
    if not _SDK_AVAILABLE:
        return None

    project  = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    api_key  = os.environ.get("GEMINI_API_KEY", "")

    if project:
        # Cloud Run / ADC path — uses Vertex AI backend
        _client = genai.Client(
            vertexai=True,
            project=project,
            location=location,
        )
    elif api_key:
        # Local dev path — uses AI Studio API key
        _client = genai.Client(api_key=api_key)
    else:
        return None

    return _client


# ── Fire Direction Prediction ─────────────────────────────────────────────────
def get_fire_direction_vertex(sensor_data: dict) -> str:
    """
    Calls Gemma 4 on Vertex AI with a sensor snapshot.
    Falls back to heuristic if SDK / credentials unavailable.

    sensor_data keys: tick, fire_cells, temperature_snapshot, smoke_snapshot
    """
    client = _get_client()
    if client is None:
        return _heuristic_direction(sensor_data)

    fire_cells = sensor_data.get("fire_cells", [])
    tick       = sensor_data.get("tick", 0)
    temp_snap  = sensor_data.get("temperature_snapshot", {})
    smoke_snap = sensor_data.get("smoke_snapshot", {})

    prompt = f"""You are an AI fire-behaviour analyst for a hospital crisis system.

SENSOR SNAPSHOT — Tick {tick}:
- Active fire cells: {len(fire_cells)} cells
- Fire locations (sample): {json.dumps(fire_cells[:8])}
- Temperature hotspots (°C): {json.dumps(temp_snap)}
- Smoke density (0-1 scale): {json.dumps(smoke_snap)}

In exactly 2 sentences:
1. State the dominant fire-spread direction (North/South/East/West/Radial) and the reason.
2. Name one zone at immediate risk and advise the crisis coordinator on the next action.

Be authoritative. No disclaimers."""

    try:
        response = client.models.generate_content(
            model="gemma-3-27b-it",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.25,
                max_output_tokens=160,
            ),
        )
        return response.text.strip()
    except Exception as exc:
        return f"[Vertex AI error: {exc}] " + _heuristic_direction(sensor_data)


def _heuristic_direction(sensor_data: dict) -> str:
    fire_cells = sensor_data.get("fire_cells", [])
    if not fire_cells:
        return "No active fire detected."

    xs = [c["x"] if isinstance(c, dict) else c[0] for c in fire_cells]
    ys = [c["y"] if isinstance(c, dict) else c[1] for c in fire_cells]
    cx, cy = sum(xs)/len(xs), sum(ys)/len(ys)

    recent = fire_cells[-min(4, len(fire_cells)):]
    rxs = [c["x"] if isinstance(c, dict) else c[0] for c in recent]
    rys = [c["y"] if isinstance(c, dict) else c[1] for c in recent]
    ncx, ncy = sum(rxs)/len(rxs), sum(rys)/len(rys)

    hdir = "East" if ncx > cx + 0.3 else ("West"  if ncx < cx - 0.3 else "")
    vdir = "South" if ncy > cy + 0.3 else ("North" if ncy < cy - 0.3 else "")
    direction = f"{vdir}-{hdir}".strip("-") or "Radial"

    return (
        f"Heuristic analysis: fire spreading {direction} — "
        f"centroid at ({round(cx,1)}, {round(cy,1)}). "
        f"Zones in the {direction} quadrant require immediate evacuation priority."
    )
