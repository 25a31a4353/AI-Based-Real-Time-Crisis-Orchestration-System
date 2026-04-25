import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import json

# Your existing simulation imports
from simulation.simulation_engine import Simulation, Building, Patient, Staff
from assignment.assignment_engine import run_assignment
from decision.decision_engine import run_decision_engine

app = FastAPI()

# --- 1. INITIALIZE SIMULATION STATE ---
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

# --- 2. SERVE THE UI (This fixes the "Not Found" error) ---
# Ensure the 'static' folder exists in your directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

# --- 3. API ENDPOINT FOR THE DASHBOARD ---
@app.post("/api/tick")
async def simulate_tick():
    if sim.rescued_count + sim.failed_count >= len(sim.patients):
        return {"status": "complete", "message": "All patients accounted for."}

    sim.update_fire()
    prioritized_patients = run_decision_engine(sim)
    assignment_results = run_assignment(sim, prioritized_patients)
    
    # Update Staff Paths from assignment
    for assignment in assignment_results["assignments"]:
        s = next((s for s in sim.staff if s.id == assignment["staff_id"]), None)
        p = next((p for p in sim.patients if p.id == assignment["patient_id"]), None)
        if s and p:
            s.path = p.path 

    # Move logic
    for s in sim.staff:
        if s.assigned_patient_id is not None and s.path:
            s.x, s.y = s.path.pop(0)

    return {
        "tick": sim.tick,
        "rescued_count": sim.rescued_count,
        "survival_rate": sim.get_survival_rate(),
        "reasoning": f"Tick {sim.tick}: Successfully managing crisis orchestration."
    }

# Start with: uvicorn main:app --host 0.0.0.0 --port 8080 (Cloud Run does this automatically)