def get_firefighter_briefing(simulation):
    """
    Firefighter Integration (from design notes):
    When firefighters arrive, they connect to the system and receive:
      1. Live fire map summary
      2. High-priority zones
      3. Safest entry paths
      4. Critical patients needing immediate help
      5. Coordinated action with internal staff

    Benefit: No time wasted understanding building layout.
    """
    fire_cells   = simulation.fire
    fire_severity = simulation.fire_severity

    # ── High-priority fire zones (severity ≥ 3) ──────────
    hot_zones = [
        {"cell": (x, y), "severity": sev, "label": f"SEVERITY {sev}"}
        for (x, y, *_), sev in fire_severity.items() if sev >= 3
    ]
    hot_zones.sort(key=lambda z: -z["severity"])

    # ── Safe entry points ─────────────────────────────────
    safe_entries = simulation.get_safe_entry_points()

    # Sort entries: furthest from fire centroid = safest
    if fire_cells and safe_entries:
        fcx = sum(x for x,y,*_ in fire_cells) / len(fire_cells)
        fcy = sum(y for x,y,*_ in fire_cells) / len(fire_cells)
        safe_entries.sort(
            key=lambda e: -(abs(e[0]-fcx) + abs(e[1]-fcy))
        )

    recommended_entry = safe_entries[0] if safe_entries else None

    # ── Critical patients needing FF assistance ───────────
    critical_patients = []
    for p in simulation.patients:
        if p.evacuated:
            continue
        fire_dist = min(
            (abs(p.x - fx) + abs(p.y - fy) for fx,fy,*_ in fire_cells),
            default=999
        )
        pfl = min(getattr(p,'floor',0), simulation.building.floors-1)
        smoke_lvl = simulation.smoke_map[pfl][p.y][p.x]
        # Flag ICU patients near fire, OR any patient in heavy smoke
        if (not p.movable and fire_dist <= 5) or smoke_lvl > 0.6:
            critical_patients.append({
                "patient_id":  p.id,
                "location":    (p.x, p.y),
                "fire_distance": fire_dist,
                "smoke_level": round(smoke_lvl, 2),
                "type":        "ICU" if not p.movable else "Mobile",
                "urgency":     "IMMEDIATE" if fire_dist <= 2 else "HIGH",
            })
    critical_patients.sort(key=lambda x: (x["fire_distance"], -x["smoke_level"]))

    # ── Fire spread direction ─────────────────────────────
    if len(fire_cells) >= 4:
        xs = [x for x,y,*_ in fire_cells]
        ys = [y for x,y,*_ in fire_cells]
        cx, cy = sum(xs)/len(xs), sum(ys)/len(ys)
        new_cells = fire_cells[-min(4,len(fire_cells)):]
        ncx = sum(x for x,y,*_ in new_cells)/len(new_cells)
        ncy = sum(y for x,y,*_ in new_cells)/len(new_cells)
        hdir = "East" if ncx > cx else ("West" if ncx < cx else "")
        vdir = "South" if ncy > cy else ("North" if ncy < cy else "")
        direction = f"{vdir}-{hdir}".strip("-") or "Radial"
    else:
        direction = "Expanding radially"

    # ── Predicted spread in next 3 ticks ──────────────────
    predicted = simulation.predict_fire_spread(ticks_ahead=3)

    return {
        "tick":                   simulation.tick,
        "fire_cell_count":        len(fire_cells),
        "hot_zones":              hot_zones[:5],
        "safe_entry_points":      safe_entries[:4],
        "recommended_entry":      recommended_entry,
        "critical_patients":      critical_patients,
        "fire_spread_direction":  direction,
        "predicted_fire_cells":   predicted,
        "internal_staff_count":   len(simulation.staff),
        "summary": (
            f"Tick {simulation.tick} | "
            f"{len(fire_cells)} active fire cells | "
            f"Spreading {direction} | "
            f"Recommended entry: {recommended_entry} | "
            f"{len(critical_patients)} critical patients need FF support"
        ),
    }


