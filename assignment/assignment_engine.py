import heapq

def _manhattan(ax, ay, bx, by):
    return abs(ax - bx) + abs(ay - by)

def find_path(start, end, simulation, risk_threshold=95):
    """
    A* algorithm to find the shortest SAFE path.
    Penalizes fire proximity and smoke density.
    Returns (path, total_risk) or (None, inf)
    """
    W, H = simulation.building.width, simulation.building.height
    fire_set = set(simulation.fire)
    
    queue = [(0, start, [])]
    visited = set()
    
    while queue:
        (cost, current, path) = heapq.heappop(queue)
        
        if current in visited:
            continue
        
        visited.add(current)
        path = path + [current]
        
        if current == end:
            return path, cost
        
        cx, cy = current
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = cx + dx, cy + dy
            
            if 0 <= nx < W and 0 <= ny < H:
                if (nx, ny) in fire_set:
                    continue # Hard constraint: No fire cells
                
                # Risk calculation
                smoke = simulation.smoke_map[ny][nx]
                temp = simulation.temperature_map[ny][nx]
                
                # Penalty for fire proximity
                min_fire_dist = min([abs(nx-fx) + abs(ny-fy) for fx, fy in fire_set], default=99)
                fire_penalty = 40 / max(min_fire_dist, 1) if min_fire_dist <= 1 else 0
                
                step_risk = 1 + (smoke * 15) + (max(0, temp - 50) * 0.3) + fire_penalty
                
                if step_risk > risk_threshold:
                    continue 
                
                heapq.heappush(queue, (cost + step_risk, (nx, ny), path))
                
    return None, float("inf")

def run_assignment(simulation, decisions):
    assignments = []
    cancelled_assignments = []
    unreachable_patients = []
    
    # ── [1] Dynamic Reassignment Check ────────────────
    for p in simulation.patients:
        if p.status == "assigned" and p.assigned_staff_id is not None:
            staff = next((s for s in simulation.staff if s.id == p.assigned_staff_id), None)
            if staff:
                new_path, risk = find_path((staff.x, staff.y), (p.x, p.y), simulation)
                if not new_path:
                    cancelled_assignments.append({
                        "patient_id": p.id,
                        "staff_id": staff.id,
                        "reason": "Path blocked by fire"
                    })
                    p.status = "waiting"
                    p.assigned_staff_id = None
                    staff.assigned_patient_id = None
                    staff.load = max(0, staff.load - 1)

    # ── [2] New Assignments ───────────────────────────
    used_staff = {s.id for s in simulation.staff if s.assigned_patient_id is not None}
    
    for d in decisions:
        p_id = d["patient_id"]
        patient = next((p for p in simulation.patients if p.id == p_id), None)
        
        if not patient or patient.evacuated or patient.status != "waiting":
            continue

        best_staff = None
        best_path_to_patient = None
        best_path_to_exit = None
        min_total_risk = float("inf")
        
        is_emergency = d["explanation"]["min_fire_dist"] <= 1 or d["priority"] > 80

        for s in simulation.staff:
            if s.id in used_staff:
                continue
            
            path_to_p, risk_to_p = find_path((s.x, s.y), (patient.x, patient.y), simulation)
            if not path_to_p:
                continue
            
            best_exit_path = None
            min_exit_risk = float("inf")
            for exit_pos in simulation.building.exits:
                path_to_e, risk_to_e = find_path((patient.x, patient.y), exit_pos, simulation)
                if path_to_e and risk_to_e < min_exit_risk:
                    best_exit_path = path_to_e
                    min_exit_risk = risk_to_e
            
            if not best_exit_path:
                continue
            
            total_risk = risk_to_p + min_exit_risk
            if not patient.movable and not s.trained:
                total_risk += 100
            
            if total_risk < min_total_risk:
                min_total_risk = total_risk
                best_staff = s
                best_path_to_patient = path_to_p
                best_path_to_exit = best_exit_path

        if best_staff:
            patient.status = "assigned"
            patient.assigned_staff_id = best_staff.id
            patient.path = best_path_to_patient + best_path_to_exit[1:]
            
            best_staff.assigned_patient_id = patient.id
            best_staff.load += 1
            used_staff.add(best_staff.id)
            
            assignments.append({
                "patient_id": patient.id,
                "staff_id": best_staff.id,
                "priority_score": d["priority"],
                "reason": [
                    f"Risk={round(min_total_risk, 1)}",
                    "Emergency override" if is_emergency else "Optimal path"
                ],
                "expected_outcome": "rescued" if min_total_risk < 150 else "high risk"
            })
        else:
            patient.status = "waiting"
            # Identify fire blocking cells (near patient)
            blocking = [(fx, fy) for fx, fy in simulation.fire 
                        if abs(fx - patient.x) + abs(fy - patient.y) <= 3]
            unreachable_patients.append({
                "patient_id": patient.id,
                "blocking_cells": blocking
            })

    return {
        "tick": simulation.tick,
        "assignments": assignments,
        "cancelled_assignments": cancelled_assignments,
        "unreachable_patients": unreachable_patients,
        "summary": {
            "assigned": len(assignments),
            "unreachable": len(unreachable_patients),
            "active_tasks": sum(1 for s in simulation.staff if s.assigned_patient_id is not None),
            "rescued_count": simulation.rescued_count,
            "failed_count": simulation.failed_count,
            "survival_rate": simulation.get_survival_rate()
        }
    }