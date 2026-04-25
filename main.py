import os
import json
import httpx # Use httpx for async API calls
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Your existing simulation imports
from simulation.simulation_engine import Simulation, Building, Patient, Staff
from assignment.assignment_engine import run_assignment
from decision.decision_engine import run_decision_engine

app = FastAPI()

# --- 1. GLOBAL STATE (Your simulation setup) ---
building = Building(10, 10)
patients = [
    Patient(0, 9, 2, movable=True,  condition="stable"),
    Patient(1, 2, 7, movable=False, condition="critical"),
    Patient(2, 1, 7, movable=True,  condition="stable"),
    Patient(3, 8, 2, movable=False, condition="critical"),
    Patient(4, 6, 2, movable=False, condition="stable"),
]
staff = [
    Staff(0, 2, 4, trained=True,  role="medic"),
    Staff(1, 5, 5, trained=False, role="nurse"),
    Staff(2, 7, 5, trained=True,  role="medic"),
]
sim = Simulation(building, patients, staff)
sim.add_firefighter(0, 0)
sim.add_firefighter(9, 9)

# --- 2. ANTIGRAVITY AI INTEGRATION ---
API_KEY = os.getenv("GOOGLE_API_KEY")

async def get_antigravity_reasoning(data_summary):
    """Calls Gemini to act as the Antigravity Orchestrator"""
    if not API_KEY:
        print("[DEBUG] GOOGLE_API_KEY environment variable not set. Using local fallback.")
        return "Orchestrator (Local Fallback): Maintain current rescue vectors. Prioritize high-risk zones."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    prompt = f"System Status: {data_summary}. Provide a 1-sentence strategic instruction for the rescue teams."
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    print(f"[DEBUG] Calling Antigravity AI (Gemini 1.5) -> Summary: {data_summary}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                print("[DEBUG] AI Response SUCCESS (200 OK)")
                return response.json()['candidates'][0]['content']['parts'][0]['text']
            else:
                print(f"[DEBUG] AI Response FAILED with status {response.status_code}")
                return "Orchestrator (Local Fallback): Maintain current rescue vectors. Prioritize high-risk zones."
        except Exception as e:
            print(f"[DEBUG] AI Request EXCEPTION: {str(e)}")
            return "Orchestrator (Local Fallback): Maintain current rescue vectors. Prioritize high-risk zones."

# --- 3. WEB ROUTES ---
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

@app.post("/api/tick")
async def simulate_tick():
    # This is your 'for tick in range(20)' logic, but one step at a time
    sim.update_fire()
    prioritized_patients = run_decision_engine(sim)
    assignment_results = run_assignment(sim, prioritized_patients)
    
    # Firefighter coordination
    ff_idx = 0
    for u in assignment_results["unreachable_patients"]:
        if ff_idx < len(sim.firefighters) and u["blocking_cells"]:
            sim.firefighters[ff_idx].assigned_zone = u["blocking_cells"][0]
            ff_idx += 1

    # Update Paths & Move (from your move_entities logic)
    for assignment in assignment_results["assignments"]:
        s = next((s for s in sim.staff if s.id == assignment["staff_id"]), None)
        p = next((p for p in sim.patients if p.id == assignment["patient_id"]), None)
        if s and p: s.path = p.path
    
    # Move one step
    for s in sim.staff:
        if s.assigned_patient_id is not None and s.path:
            s.x, s.y = s.path.pop(0)

    # Call the AI for the dashboard text
    status_summary = f"Tick {sim.tick}, {sim.rescued_count} rescued, {len(sim.fire)} fire cells"
    ai_reasoning = await get_antigravity_reasoning(status_summary)

    # Enrich state for UI
    patients_data = []
    for p in sim.patients:
        patients_data.append({
            "id": p.id,
            "x": p.x, "y": p.y,
            "condition": p.condition,
            "movable": p.movable,
            "rescued": p.rescued,
            "risk_score": round(100 + (p.y * 20.5) if not p.rescued else 0, 1),
            "temp": 20 + len(sim.fire),
            "smoke": round(len(sim.fire) * 0.05, 2)
        })

    return {
        "tick": sim.tick,
        "rescued_count": sim.rescued_count,
        "survival_rate": sim.get_survival_rate(),
        "ai_logic": ai_reasoning,
        "fire_cells": len(sim.fire),
        "fire_coords": list(sim.fire),
        "patients": patients_data,
        "staff": [{"id": s.id, "x": s.x, "y": s.y, "role": s.role} for s in sim.staff],
        "assignments": assignment_results["assignments"]
    }

if __name__ == "__main__":
    import uvicorn
    print("\n[SYSTEM] Starting Crisis Orchestration UI locally...")
    print("[SYSTEM] Access dashboard at: http://localhost:8000\n")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)