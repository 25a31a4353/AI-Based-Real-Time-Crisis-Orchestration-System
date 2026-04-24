class VerificationEngine:
    """
    Verification Layer — ensures tasks are actually completed.

    Key insight: We cannot trust human reporting alone.
    We use staff location + smoke/fire data to probabilistically
    verify whether a rescue was completed.

    Logic (from design notes):
      IF staff within 2 cells of patient AND area moving toward safe zone
          → mark likely_complete (with confidence score)
      IF tick > deadline AND patient still in danger zone
          → mark FAILED → trigger reassignment
    """

    def __init__(self, deadline_ticks=3):
        self.tasks        = {}      # task_id → task dict
        self.task_counter = 0
        self.deadline_ticks = deadline_ticks

    def register_assignments(self, assignments_data, current_tick):
        """Call this every tick after run_assignment()."""
        for a in assignments_data.get("assignments", []):
            # Avoid re-registering the same staff→patient pair
            already = any(
                t["staff_id"] == a["staff_id"] and t["patient_id"] == a["patient_id"]
                and t["status"] == "active"
                for t in self.tasks.values()
            )
            if already:
                continue

            tid = f"T{self.task_counter:03d}"
            self.task_counter += 1
            self.tasks[tid] = {
                "task_id":      tid,
                "staff_id":     a["staff_id"],
                "patient_id":   a["patient_id"],
                "assigned_tick": current_tick,
                "deadline_tick": current_tick + self.deadline_ticks,
                "status":       "active",   # active | likely_complete | completed | failed
                "confidence":   1.0,
                "fail_reason":  "",
            }

    def verify_tick(self, simulation, current_tick):
        """Run verification for this tick. Returns reassignment list."""
        reassign_list   = []
        newly_completed = []
        newly_failed    = []

        for tid, task in self.tasks.items():
            if task["status"] not in ("active",):
                continue

            pid  = task["patient_id"]
            sid  = task["staff_id"]

            patient = next((p for p in simulation.patients if p.id == pid), None)
            staff   = next((s for s in simulation.staff   if s.id == sid), None)

            if patient is None or staff is None:
                task["status"] = "completed"
                continue

            if patient.evacuated:
                task["status"]     = "completed"
                task["confidence"] = 1.0
                newly_completed.append(tid)
                continue

            dist_to_patient = abs(staff.x - patient.x) + abs(staff.y - patient.y)
            fire_near_patient = any(
                abs(patient.x - fx) + abs(patient.y - fy) <= 1
                for fx, fy in simulation.fire
            )
            smoke_at_patient = simulation.smoke_map[patient.y][patient.x]

            # ── Likely complete? ──────────────────────────
            if dist_to_patient <= 2 and not fire_near_patient:
                # Confidence: decreases with distance and smoke
                conf = max(0.0, 1.0 - dist_to_patient*0.12 - smoke_at_patient*0.25)
                task["confidence"] = round(conf, 2)
                if conf >= 0.55:
                    task["status"] = "likely_complete"
                    newly_completed.append(tid)

            # ── Failed (deadline exceeded + patient still in danger) ──
            elif current_tick > task["deadline_tick"]:
                if fire_near_patient or smoke_at_patient > 0.45:
                    task["status"]     = "failed"
                    task["fail_reason"] = (
                        f"Deadline exceeded at tick {current_tick} "
                        f"(deadline was {task['deadline_tick']})"
                    )
                    newly_failed.append(tid)
                    reassign_list.append({
                        "patient_id": pid,
                        "task_id":    tid,
                        "reason":     task["fail_reason"],
                    })
                else:
                    # Deadline passed but patient is now safe
                    task["status"] = "completed"
                    newly_completed.append(tid)

            # ── Update confidence decay ───────────────────
            else:
                ticks_left = task["deadline_tick"] - current_tick
                task["confidence"] = round(ticks_left / max(self.deadline_ticks, 1), 2)

        return {
            "reassign_needed": reassign_list,
            "completed":       newly_completed,
            "failed":          newly_failed,
            "all_tasks":       dict(self.tasks),
        }

    def summary(self):
        counts = {"active": 0, "likely_complete": 0, "completed": 0, "failed": 0}
        for t in self.tasks.values():
            s = t["status"]
            if s in counts:
                counts[s] += 1
            else:
                counts["active"] += 1
        counts["total"] = len(self.tasks)
        return counts
