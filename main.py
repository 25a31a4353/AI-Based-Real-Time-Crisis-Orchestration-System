from simulation.simulation_engine import Simulation, Building, Patient, Staff
from assignment.assignment_engine import run_assignment
from decision.decision_engine import run_decision_engine

import random
import json

# BUILDING
building = Building(10, 10)

# PATIENTS
patients = [
    Patient(0, 9, 2, movable=True,  condition="stable"),
    Patient(1, 2, 7, movable=False, condition="critical"),
    Patient(2, 1, 7, movable=True,  condition="stable"),
    Patient(3, 8, 2, movable=False, condition="critical"),
    Patient(4, 6, 2, movable=False, condition="stable"),
]

# STAFF
staff = [
    Staff(0, 2, 4, trained=True,  role="medic"),
    Staff(1, 5, 5, trained=False, role="nurse"),
    Staff(2, 7, 5, trained=True,  role="medic"),
]

# SIMULATION
sim = Simulation(building, patients, staff)

# Add Firefighters
sim.add_firefighter(0, 0)
sim.add_firefighter(9, 9)

def move_entities(sim):
    """Move staff along their assigned paths and update patient status."""
    for s in sim.staff:
        if s.assigned_patient_id is not None:
            p = next((p for p in sim.patients if p.id == s.assigned_patient_id), None)
            if not p or p.status == "failed":
                s.assigned_patient_id = None
                s.path = []
                continue
                
            if s.path:
                # Move to next cell in path
                next_pos = s.path.pop(0)
                s.x, s.y = next_pos
                
                # If staff reached patient
                if (s.x, s.y) == (p.x, p.y):
                    p.status = "in_progress"
                
                # If patient is with staff and they reached an exit
                if p.status == "in_progress" and (s.x, s.y) in sim.building.exits:
                    p.status = "rescued"
                    p.evacuated = True
                    sim.rescued_count += 1
                    s.assigned_patient_id = None
                    s.path = []
                    s.load = max(0, s.load - 1)

def coordinate_firefighters(sim, unreachable_patients):
    """Assign firefighters to unblock paths for unreachable patients."""
    ff_idx = 0
    for u in unreachable_patients:
        if ff_idx >= len(sim.firefighters):
            break
        if u["blocking_cells"]:
            # Assign firefighter to the first blocking cell
            sim.firefighters[ff_idx].assigned_zone = u["blocking_cells"][0]
            ff_idx += 1

for tick in range(20):
    sim.update_fire()
    
    # Prioritize Patients
    prioritized_patients = run_decision_engine(sim)
    
    # Run Assignment
    assignment_results = run_assignment(sim, prioritized_patients)
    
    # Coordinate Firefighters
    coordinate_firefighters(sim, assignment_results["unreachable_patients"])
    
    # Update Staff Paths (from assignment results if new)
    for assignment in assignment_results["assignments"]:
        s = next((s for s in sim.staff if s.id == assignment["staff_id"]), None)
        p = next((p for p in sim.patients if p.id == assignment["patient_id"]), None)
        if s and p:
            s.path = p.path # Patient path was computed in run_assignment
    
    # Move entities
    move_entities(sim)
    
    # Predicted fire for the output
    predicted_fire = sim.predict_fire_spread(ticks_ahead=3)
    
    # Final Output Formatting
    output = {
        "tick": sim.tick,
        "fire_cells": list(sim.fire),
        "predicted_fire": predicted_fire,
        "prioritized_patients": [
            {
                "patient_id": p["patient_id"],
                "priority_score": p["priority"],
                "reason": [
                    f"Risk: {p['explanation']['priority_level']}",
                    f"ICU" if p['is_icu'] else "Mobile",
                    f"Fire dist: {p['explanation']['min_fire_dist']}"
                ],
                "expected_outcome": "rescued" if p["priority"] < 60 else "high risk"
            } for p in prioritized_patients
        ],
        "assignments": assignment_results["assignments"],
        "cancelled_assignments": assignment_results["cancelled_assignments"],
        "rescued_count": sim.rescued_count,
        "failed_count": sim.failed_count,
        "survival_rate": sim.get_survival_rate(),
        "system_decision_reasoning": f"Tick {sim.tick}: Managing {sim.get_in_progress_count()} active rescues. "
                                     f"Coordinating {len(sim.firefighters)} firefighters to unblock paths for "
                                     f"{len(assignment_results['unreachable_patients'])} unreachable patients."
    }
    
    print(json.dumps(output, indent=2))
    
    if sim.rescued_count + sim.failed_count == len(sim.patients):
        print("\n=== ALL PATIENTS ACCOUNTED FOR ===")
        break

print("\n=== SIMULATION COMPLETE ===")