import sys; sys.path.insert(0, '.')
from simulation.simulation_engine import Simulation, Building, Patient, Staff
from decision.gemma_decision_engine import run_decision_engine_gemma
from assignment.assignment_engine import run_assignment
from verification.verification_engine import VerificationEngine
from planner.simulation_planner import run_planner
from firefighter.firefighter_module import get_firefighter_briefing

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
verif = VerificationEngine(deadline_ticks=3)

for tick in range(3):
    sim.update_fire()
    result = run_decision_engine_gemma(sim)
    decisions = result["decisions"]
    ai_dir = result["ai_fire_direction"]
    assignments = run_assignment(sim, decisions)
    verif.register_assignments(assignments, sim.tick)
    verification = verif.verify_tick(sim, sim.tick)
    plan = run_planner(sim)
    ff = get_firefighter_briefing(sim)
    n_assigned = len(assignments["assignments"])
    print(f"Tick {sim.tick}: fire={len(sim.fire)} cells | assigned={n_assigned} | AI: {ai_dir[:70]}...")

print()
print("=== PRIORITY SCORES (Tick 3) ===")
for d in decisions:
    label = "ICU" if d["is_icu"] else "Mobile"
    print(f"  Patient {d['patient_id']} [{label}]: score={d['priority']} level={d['explanation']['priority_level']}")

print()
print("=== VERIFICATION SUMMARY ===")
print(verif.summary())
print()
print("ALL SYSTEMS OPERATIONAL - No errors.")
