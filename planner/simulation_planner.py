def _predict_fire_n(fire_cells, fire_severity, width, height, n):
    """Fast fire spread prediction without modifying real simulation."""
    predicted = set(tuple(c) for c in fire_cells)
    current = set(tuple(c) for c in fire_cells)
    dirs = [(1,0),(-1,0),(0,1),(0,-1)]
    for _ in range(n):
        nxt = set()
        for fx, fy in current:
            for dx, dy in dirs:
                nx, ny = fx+dx, fy+dy
                if 0 <= nx < width and 0 <= ny < height and (nx,ny) not in predicted:
                    nxt.add((nx,ny))
        predicted |= nxt
        current = nxt
    return predicted   # all cells including current fire

def _patient_risk_after_plan(patient, future_fire, fire_severity):
    """Estimate individual patient risk under a predicted fire scenario."""
    dist = min(
        (abs(patient.x - fx) + abs(patient.y - fy) for fx, fy in future_fire),
        default=999
    )
    base_risk = max(0, 10 - dist)
    # ICU patients have higher exposure weight
    if not patient.movable:
        base_risk *= 1.6
    return round(base_risk, 2)

def run_planner(simulation, ticks_ahead=3):
    """
    Simulation-Based Decision Engine (KEY INNOVATION from design notes).

    Before executing any response, the AI simulates 3 different plans
    and selects the one with the highest survival probability.

    Plan A — Patient First   : send all staff to highest-priority patients immediately
    Plan B — Fire Control    : divert 1 staff to slow fire spread, rest rescue patients
    Plan C — Evacuate Mobile : mobile patients cleared first → free corridors for ICU rescue

    Returns ranked plans with survival probability for each.
    """
    W = simulation.building.width
    H = simulation.building.height

    # Future fire under no intervention
    future_fire = _predict_fire_n(
        simulation.fire, simulation.fire_severity, W, H, ticks_ahead
    )

    patients = [p for p in simulation.patients if not p.evacuated]
    if not patients:
        return {"plans": [], "recommended_plan": None, "reasoning": "No patients to evaluate."}

    results = []

    # ── PLAN A: Patient First ─────────────────────────────────
    # Staff immediately dispatched to critical patients.
    # Fire continues spreading unhindered.
    a_fire   = future_fire
    a_risks  = [_patient_risk_after_plan(p, a_fire, simulation.fire_severity) for p in patients]
    # Reduce risk for top 3 patients (staff reached them)
    a_risks_sorted = sorted(enumerate(a_risks), key=lambda x: -x[1])
    a_risks_adj = list(a_risks)
    for rank, (idx, _) in enumerate(a_risks_sorted[:len(simulation.staff)]):
        reduction = max(0.5, 1.0 - rank*0.15)   # first staff = 50% risk reduction
        a_risks_adj[idx] *= (1 - reduction)
    a_total   = round(sum(a_risks_adj), 2)
    a_surv    = round(max(0, 1 - a_total / max(len(patients)*10, 1)) * 100, 1)
    a_at_risk = sum(1 for r in a_risks_adj if r > 2)

    results.append({
        "plan_key":               "patient_first",
        "name":                   "Plan A — Patient First",
        "icon":                   "🏥",
        "description":            "Dispatch all staff directly to highest-priority patients. Fire spreads uncontrolled.",
        "survival_probability":   a_surv,
        "patients_at_risk":       a_at_risk,
        "total_risk_score":       a_total,
        "fire_cells_predicted":   len(a_fire),
        "tradeoff":               "Fast rescue but fire may cut off escape routes.",
    })

    # ── PLAN B: Fire Control First ────────────────────────────
    # 1 staff diverts to fire → spread reduced by ~35% for next 3 ticks.
    # Remaining staff rescue patients.
    b_fire_raw = _predict_fire_n(
        simulation.fire, simulation.fire_severity, W, H, ticks_ahead
    )
    # Simulate containment: fire spread ~35% smaller
    fire_list  = list(simulation.fire)
    b_fire_contained = set(fire_list[:max(1, int(len(b_fire_raw)*0.65))])
    b_fire_contained |= set(simulation.fire)
    b_risks     = [_patient_risk_after_plan(p, b_fire_contained, simulation.fire_severity) for p in patients]
    b_risks_sorted = sorted(enumerate(b_risks), key=lambda x: -x[1])
    b_risks_adj = list(b_risks)
    # One fewer staff for rescue (one diverted to fire)
    available_staff = max(0, len(simulation.staff) - 1)
    for rank, (idx, _) in enumerate(b_risks_sorted[:available_staff]):
        reduction = max(0.5, 1.0 - rank*0.15)
        b_risks_adj[idx] *= (1 - reduction)
    b_total   = round(sum(b_risks_adj), 2)
    b_surv    = round(max(0, 1 - b_total / max(len(patients)*10, 1)) * 100, 1)
    b_at_risk = sum(1 for r in b_risks_adj if r > 2)

    results.append({
        "plan_key":               "fire_control",
        "name":                   "Plan B — Fire Control First",
        "icon":                   "🔥",
        "description":            "1 staff diverts to contain fire spread. Reduces future fire zone by ~35%.",
        "survival_probability":   b_surv,
        "patients_at_risk":       b_at_risk,
        "total_risk_score":       b_total,
        "fire_cells_predicted":   len(b_fire_contained),
        "tradeoff":               "Slower patient rescue but safer corridors long-term.",
    })

    # ── PLAN C: Evacuate Mobile Patients First ────────────────
    # Clear mobile patients from corridors first → frees paths for ICU rescue.
    mobile  = [p for p in patients if p.movable]
    icu_pts = [p for p in patients if not p.movable]
    c_risks_adj = []
    for p in patients:
        base = _patient_risk_after_plan(p, future_fire, simulation.fire_severity)
        if p.movable:
            base *= 0.3    # mobile patients largely safe once evacuated
        else:
            base *= 1.1    # ICU patients wait slightly longer
        c_risks_adj.append(base)
    c_total   = round(sum(c_risks_adj), 2)
    c_surv    = round(max(0, 1 - c_total / max(len(patients)*10, 1)) * 100, 1)
    c_at_risk = sum(1 for r in c_risks_adj if r > 2)

    results.append({
        "plan_key":               "evacuate_mobile",
        "name":                   "Plan C — Evacuate Mobile First",
        "icon":                   "🚶",
        "description":            f"Clear {len(mobile)} mobile patients first to free corridors for {len(icu_pts)} ICU rescues.",
        "survival_probability":   c_surv,
        "patients_at_risk":       c_at_risk,
        "total_risk_score":       c_total,
        "fire_cells_predicted":   len(future_fire),
        "tradeoff":               "Clears congestion but ICU patients wait longer.",
    })

    # ── Select best plan ──────────────────────────────────────
    best = max(results, key=lambda x: x["survival_probability"])
    for r in results:
        r["recommended"] = (r["plan_key"] == best["plan_key"])

    # Build reasoning string
    others = [r for r in results if not r["recommended"]]
    reasoning = (
        f"AI selected '{best['name']}' — survival probability {best['survival_probability']}% "
        f"vs {others[0]['name']} ({others[0]['survival_probability']}%) "
        f"and {others[1]['name']} ({others[1]['survival_probability']}%). "
        f"System will now execute this plan."
    )

    return {
        "plans":              results,
        "recommended_plan":   best,
        "reasoning":          reasoning,
    }
