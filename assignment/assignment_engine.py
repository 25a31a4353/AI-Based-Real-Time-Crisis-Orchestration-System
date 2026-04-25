def _manhattan(ax, ay, bx, by):
    return abs(ax - bx) + abs(ay - by)

def _path_risk(sx, sy, px, py, simulation):
    """Estimate danger level of the straight-line path between staff and patient."""
    steps = max(abs(sx - px), abs(sy - py), 1)
    risk  = 0.0
    fire_set = set((x,y) for x,y,*_ in simulation.fire)

    for i in range(steps + 1):
        t  = i / steps
        cx = round(sx + t * (px - sx))
        cy = round(sy + t * (py - sy))
        cx = max(0, min(cx, simulation.building.width  - 1))
        cy = max(0, min(cy, simulation.building.height - 1))

        if (cx, cy) in fire_set:
            sev   = simulation.fire_severity.get((cx, cy), 1)
            risk += 25 * sev

        fl = 0
        smoke = simulation.smoke_map[fl][cy][cx]
        risk += smoke * 8

        temp = simulation.temperature_map[fl][cy][cx]
        if temp > 50:
            risk += (temp - 50) * 0.25

    return round(risk, 1)

def run_assignment(simulation, decisions,
                   alpha=1.0, beta=0.7, gamma=0.4, delta=1.3):
    """
    Assignment Cost: A = α·Distance + β·PathRisk + γ·Load − δ·SkillMatch
    Objective: minimise total rescue cost across all assignments.

    α=1.0  Distance   → travel time
    β=0.7  PathRisk   → fire/smoke on route
    γ=0.4  Load       → avoid overloading one staff member
    δ=1.3  SkillMatch → big reward for sending ICU-trained staff to ICU patient
    """
    assignments = []
    used_staff  = set()

    for d in decisions:
        patient = next((p for p in simulation.patients if p.id == d["patient_id"]), None)
        if patient is None or patient.evacuated:
            continue

        best_staff = None
        best_cost  = float("inf")
        best_breakdown = {}

        for s in simulation.staff:
            if s.id in used_staff:
                continue

            dist      = _manhattan(s.x, s.y, patient.x, patient.y)
            path_risk = _path_risk(s.x, s.y, patient.x, patient.y, simulation)
            load      = getattr(s, "load", 0)

            # Skill match bonus
            skill_bonus = 0.0
            if not patient.movable and getattr(s, "trained", False):
                skill_bonus = delta * 18      # ICU patient + trained staff
            elif not patient.movable and not getattr(s, "trained", True):
                path_risk  += 12              # Penalty: untrained for ICU

            cost = alpha*dist + beta*path_risk + gamma*load - skill_bonus

            if cost < best_cost:
                best_cost  = cost
                best_staff = s
                best_breakdown = {
                    "distance":   dist,
                    "path_risk":  path_risk,
                    "load":       load,
                    "skill_bonus": round(skill_bonus, 1),
                    "total_cost": round(cost, 1),
                }

        if best_staff:
            used_staff.add(best_staff.id)
            best_staff.load = getattr(best_staff, "load", 0) + 1

            if best_breakdown["path_risk"] > 25:
                route_note = "⚠️ Fire on route — use alternate corridor"
            elif best_breakdown["path_risk"] > 8:
                route_note = "⚠️ Smoke on path — proceed with mask"
            else:
                route_note = "✅ Route clear"

            assignments.append({
                "staff_id":      best_staff.id,
                "patient_id":    patient.id,
                "target_room":   f"({patient.x},{patient.y})",
                "cost_breakdown": best_breakdown,
                "route_note":    route_note,
                "reason": (
                    f"dist={best_breakdown['distance']} | "
                    f"risk={best_breakdown['path_risk']} | "
                    f"cost={best_breakdown['total_cost']}"
                ),
            })

    return {"assignments": assignments}
