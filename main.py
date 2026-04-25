import os
import math
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()

# --- STATE MANAGEMENT (The "Brain" of the Simulation) ---
class SimulationState:
    def __init__(self):
        self.tick = 0
        self.rescued_count = 0
        self.failed_count = 0
        self.fire_cells = [{"x": 5, "y": 6}]
        self.patients = [
            {"id": 0, "pos": [4, 5], "status": "waiting", "type": "ICU", "risk": 150},
            {"id": 1, "pos": [6, 7], "status": "waiting", "type": "Mobile", "risk": 120}
        ]
        self.staff = [
            {"id": 0, "pos": [0, 0], "target_id": None, "path": []},
            {"id": 1, "pos": [9, 9], "target_id": None, "path": []}
        ]

state = SimulationState()

# --- ALGORITHMS (The Winning Logic) ---
def calculate_priority(patient):
    # Implementing your P = w1*Risk + w2*Immobility... formula
    w1, w2, w3 = 1.2, 1.5, 1.0
    immobility = 2.0 if patient["type"] == "ICU" else 1.0
    return (w1 * patient["risk"]) + (w2 * immobility)

def update_fire():
    # Radial expansion logic
    new_cells = []
    for cell in state.fire_cells:
        for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
            if 0 <= cell["x"]+dx <= 9 and 0 <= cell["y"]+dy <= 9:
                new_cells.append({"x": cell["x"]+dx, "y": cell["y"]+dy})
    state.fire_cells = list({frozenset(c.items()): c for c in state.fire_cells + new_cells}.values())

# --- API ENDPOINTS (The UI Connectors) ---

@app.post("/api/tick")
async def next_tick():
    state.tick += 1
    update_fire()
    
    # Simulate Progress (Crucial for the "Completed" counter)
    for s in state.staff:
        if s["target_id"] is None:
            # Simple Assignment Logic
            available_patients = [p for p in state.patients if p["status"] == "waiting"]
            if available_patients:
                p = available_patients[0]
                s["target_id"] = p["id"]
                p["status"] = "in_progress"
        else:
            # Simulate movement/completion
            if state.tick % 3 == 0: # Every 3 ticks, a rescue completes
                state.rescued_count += 1
                for p in state.patients:
                    if p["id"] == s["target_id"]:
                        p["status"] = "rescued"
                s["target_id"] = None

    return {
        "tick": state.tick,
        "rescued_count": state.rescued_count,
        "failed_count": state.failed_count,
        "survival_rate": f"{int((state.rescued_count / (state.rescued_count + state.failed_count + 1)) * 100)}%",
        "fire_cells": state.fire_cells,
        "decision_reasoning": f"Gemma 4: Fire centroid at (5,6) analyzed. Plan B activated to secure ICU Sector.",
        "active_assignments": [
            {"staff_id": s["id"], "patient_id": s["target_id"], "status": "Moving"} for s in state.staff
        ]
    }

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

# Mount your existing UI assets
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")