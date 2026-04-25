import json
from simulation.simulation_engine import Simulation, Building, Patient, Staff
from verification.verification_engine import VerificationEngine

def run_verification_test():
    print("=== STARTING VERIFICATION LAYER TEST ===")
    print("Scenario: Responder is assigned a rescue but gets stuck in a corridor for 2 minutes (4 ticks).\n")
    
    # 1. Setup minimal simulation
    building = Building(10, 10)
    
    # Patient in danger zone
    patient = Patient(99, 5, 5, movable=False, condition="critical")
    
    # Staff / Responder starting far away
    staff = Staff(88, 0, 0, trained=True, role="medic")
    
    sim = Simulation(building, [patient], [staff])
    
    # Introduce fire near patient to ensure they remain in danger
    sim.fire.append((6, 5))
    sim.fire.append((5, 6))
    sim.fire_severity[(6, 5)] = 2
    sim.fire_severity[(5, 6)] = 2
    
    # 2. Setup Verification Engine (Deadline = 3 ticks)
    verifier = VerificationEngine(deadline_ticks=3)
    
    # 3. Simulate an assignment being made at Tick 0
    print("[Tick 0] System assigns Staff 88 to rescue Patient 99.")
    assignments_data = {
        "assignments": [
            {
                "staff_id": 88,
                "patient_id": 99,
                "target_room": "safe_zone"
            }
        ]
    }
    verifier.register_assignments(assignments_data, current_tick=0)
    print("Initial Tasks state:", json.dumps(verifier.summary(), indent=2))
    
    # 4. Simulate the responder being 'stuck' for 4 ticks
    for tick in range(1, 5):
        print(f"\n--- [Tick {tick}] ---")
        print("Responder is stuck at (0, 0). No movement detected.")
        
        # Ensure smoke is high at patient location to guarantee danger zone triggers
        sim.smoke_map[5][5] = 0.8
        
        # Run verification layer logic
        result = verifier.verify_tick(sim, current_tick=tick)
        
        # Print trace of task status
        for tid, tinfo in verifier.tasks.items():
            print(f"Task {tid} trace: Status='{tinfo['status']}', Confidence={tinfo.get('confidence')}")
        
        # Check if logic caught the failure
        if result["failed"]:
            print(f"\n[!] ALERT: Verification Logic Triggered -> 'Task Incomplete'")
            print(f"Reason recorded: {result['reassign_needed'][0]['reason']}")
            print("Reassignment Payload Generated:")
            print(json.dumps(result["reassign_needed"], indent=2))
            print("\n=== TEST SUCCESSFUL ===")
            print("The engine correctly identified the stuck responder, flagged the task as failed, and queued it for reassignment.")
            break

if __name__ == "__main__":
    run_verification_test()
