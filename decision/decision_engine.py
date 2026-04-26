def run_decision_engine(simulation, weights=None):
    """
    Priority Score: P = w1·Risk + w2·Immobility + w3·Urgency − w4·NearbyHelp

    w1=1.2  Risk        → fire proximity + predicted spread + heat + smoke
    w2=1.5  Immobility  → ICU patients score highest (cannot self-evacuate)
    w3=1.0  Urgency     → time before fire reaches patient
    w4=0.8  NearbyHelp  → reduces priority if staff already close
    """
    if weights is None:
        weights = {"risk": 1.2, "immobility": 1.5, "urgency": 1.0, "nearby_help": 0.8}

    w1 = weights["risk"]
    w2 = weights["immobility"]
    w3 = weights["urgency"]
    w4 = weights["nearby_help"]

    predicted_fire_raw = simulation.predict_fire_spread(ticks_ahead=3)
    predicted_fire = [(x,y) for x,y,f in predicted_fire_raw]
    predicted_set  = set(predicted_fire)

    decisions = []

    for p in simulation.patients:
        if p.evacuated:
            continue

        # ── Factor 1: RISK ─────────────────────────────────
        risk = 0.0
        for (fx, fy, f, *_) in simulation.fire:
            dist = abs(p.x - fx) + abs(p.y - fy)
            sev  = simulation.fire_severity.get((fx, fy, f), 1)
            if dist == 0:
                risk += 55 * sev
            elif dist <= 2:
                risk += (28 / dist) * sev
            elif dist <= 5:
                risk += (12 / dist) * sev

        # Predicted spread risk (discounted)
        for (fx, fy) in predicted_set:
            dist = abs(p.x - fx) + abs(p.y - fy)
            if dist <= 3:
                risk += 8 / max(dist, 1)

        # Heat contribution
        fl = min(getattr(p,'floor',0), simulation.building.floors-1)
        temp = simulation.temperature_map[fl][p.y][p.x]
        if temp > 55:
            risk += (temp - 55) * 0.6

        # Smoke contribution
        smoke = simulation.smoke_map[fl][p.y][p.x]
        risk += smoke * 18

        # ── Factor 2: IMMOBILITY ───────────────────────────
        immobility = 0.0
        if not p.movable:
            immobility = 45        # ICU — cannot escape under any circumstance
        elif getattr(p, 'condition', 'stable') == "critical":
            immobility = 20        # Needs assistance but can walk

        # ── Factor 3: URGENCY ──────────────────────────────
        min_fire_dist = min(
            (abs(p.x - fx) + abs(p.y - fy) for fx, fy, *_ in simulation.fire),
            default=999
        )
        if min_fire_dist == 0:
            urgency = 60
        elif min_fire_dist == 1:
            urgency = 45
        elif min_fire_dist == 2:
            urgency = 30
        elif min_fire_dist <= 4:
            urgency = 18
        elif min_fire_dist <= 6:
            urgency = 8
        else:
            urgency = 0

        # ── Factor 4: NEARBY HELP ─────────────────────────
        nearby_help = 0.0
        for s in simulation.staff:
            d = abs(p.x - s.x) + abs(p.y - s.y)
            if d <= 2:
                nearby_help += 18
            elif d <= 4:
                nearby_help += 8

        # ── FINAL PRIORITY ────────────────────────────────
        score = (w1*risk + w2*immobility + w3*urgency) - (w4*nearby_help)
        score = max(0.0, round(score, 1))

        if score > 80:
            level = "critical"
        elif score > 45:
            level = "high"
        elif score > 20:
            level = "medium"
        else:
            level = "low"

        decisions.append({
            "patient_id":  p.id,
            "priority":    score,
            "explanation": {
                "priority_level":   level,
                "risk_score":       round(w1 * risk, 1),
                "immobility_score": round(w2 * immobility, 1),
                "urgency_score":    round(w3 * urgency, 1),
                "nearby_help":      round(w4 * nearby_help, 1),
                "temperature":      round(temp, 1),
                "smoke_level":      round(smoke, 2),
                "min_fire_dist":    min_fire_dist,
            },
            "is_icu":                not p.movable,
            "predicted_fire_nearby": any(
                abs(p.x - fx) + abs(p.y - fy) <= 3 for fx, fy in predicted_set
            ),
        })

    decisions.sort(key=lambda x: x["priority"], reverse=True)
    return decisions
