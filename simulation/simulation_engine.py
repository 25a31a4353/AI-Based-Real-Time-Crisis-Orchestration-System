import random

class Patient:
    def __init__(self, pid, x, y, movable=True, condition="stable"):
        self.id = pid
        self.x = x
        self.y = y
        self.movable = movable          # False = ICU (immobile)
        self.condition = condition      # "stable" | "critical"
        self.evacuated = False
        self.status = "waiting"         # waiting, assigned, in_progress, rescued, failed
        self.assigned_staff_id = None
        self.path = []                  # Current path assigned

class Staff:
    def __init__(self, sid, x, y, trained=True, role="medic"):
        self.id = sid
        self.x = sid # This was sid in the original? No, it should be x.
        self.x = x
        self.y = y
        self.trained = trained          # True = ICU-trained
        self.role = role
        self.load = 0                   # active tasks assigned
        self.assigned_patient_id = None
        self.path = []

class Firefighter:
    def __init__(self, fid, entry_x, entry_y):
        self.id = fid
        self.x = entry_x
        self.y = entry_y
        self.assigned_zone = None

class Building:
    def __init__(self, width=10, height=10):
        self.width = width
        self.height = height
        self.floors = 1
        self.exits = [(0,0),(9,0),(0,9),(9,9),(4,0),(4,9)]

class Simulation:
    def __init__(self, building, patients, staff):
        self.building = building
        self.patients = patients
        self.staff = staff
        self.firefighters = []
        self.grid = [["." for _ in range(building.width)]
                     for _ in range(building.height)]
        # Heat map: 20°C baseline
        self.temperature_map = [[20.0]*building.width for _ in range(building.height)]
        # Smoke map: 0.0 (clear) → 1.0 (dense)
        self.smoke_map = [[0.0]*building.width for _ in range(building.height)]
        self.fire = []
        self.fire_severity = {}         # (x,y) → severity 1-4
        self.tick = 0
        
        # Success Tracking
        self.rescued_count = 0
        self.failed_count = 0
        
        self._init_entities()

    def _init_entities(self):
        for p in self.patients:
            self.grid[p.y][p.x] = "P"
        for s in self.staff:
            self.grid[s.y][s.x] = "S"
        # Fire origin at (9,9)
        origin = (9, 9)
        self.fire.append(origin)
        self.fire_severity[origin] = 4
        self.grid[9][9] = "F"
        self.temperature_map[9][9] = 95.0

    def get_survival_rate(self):
        total = len(self.patients)
        if total == 0: return 100.0
        return round((self.rescued_count / total) * 100, 1)

    def get_in_progress_count(self):
        return sum(1 for p in self.patients if p.status in ["assigned", "in_progress"])

    # ── Fire suppression ────────────────────────────────
    def update_firefighters(self):
        """Firefighters move and suppress fire in their assigned zones."""
        for ff in self.firefighters:
            if ff.assigned_zone:
                zx, zy = ff.assigned_zone
                # Move toward zone
                dx = 1 if zx > ff.x else -1 if zx < ff.x else 0
                dy = 1 if zy > ff.y else -1 if zy < ff.y else 0
                ff.x += dx
                ff.y += dy
                
                # Suppress fire in a 2-cell radius
                for sx in range(ff.x - 2, ff.x + 3):
                    for sy in range(ff.y - 2, ff.y + 3):
                        if (sx, sy) in self.fire_severity:
                            # Reduce severity
                            self.fire_severity[(sx, sy)] -= 4
                            if self.fire_severity[(sx, sy)] <= 0:
                                del self.fire_severity[(sx, sy)]
                                if (sx, sy) in self.fire:
                                    self.fire.remove((sx, sy))
                                self.grid[sy][sx] = "."
                                self.temperature_map[sy][sx] = max(20, self.temperature_map[sy][sx] - 50)

    # ── Fire spread ────────────────────────────────────
    def update_fire(self):
        W, H = self.building.width, self.building.height
        cardinal   = [(1,0),(-1,0),(0,1),(0,-1)]
        diagonal   = [(1,1),(-1,1),(1,-1),(-1,-1)]

        new_fire = []
        for fx, fy in self.fire:
            sev = self.fire_severity.get((fx,fy), 2)
            # Fire doesn't spread if severity is low (suppressed)
            if sev <= 1: continue
            
            dirs = cardinal if sev < 3 else cardinal + diagonal
            for dx, dy in dirs:
                if random.random() > 0.4: continue # Slow spread
                nx, ny = fx+dx, fy+dy
                if 0 <= nx < W and 0 <= ny < H and (nx,ny) not in self.fire_severity:
                    new_fire.append((nx, ny, max(1, sev-1)))

        for nx, ny, sev in new_fire:
            self.fire.append((nx, ny))
            self.fire_severity[(nx,ny)] = sev
            self.grid[ny][nx] = "F"
            self.temperature_map[ny][nx] = min(100, self.temperature_map[ny][nx] + 40)

        # Thermal radiation (2-cell radius)
        for fx, fy in self.fire:
            sev = self.fire_severity.get((fx,fy), 1)
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    nx, ny = fx+dx, fy+dy
                    if 0 <= nx < W and 0 <= ny < H:
                        dist = max(abs(dx)+abs(dy), 1)
                        self.temperature_map[ny][nx] = min(
                            100, self.temperature_map[ny][nx] + (sev*12)/dist
                        )

        # Smoke (3-cell radius, drifts south-east slightly)
        for fx, fy in self.fire:
            for dx in range(-3, 4):
                for dy in range(-3, 5):    # bias toward +y (south)
                    nx, ny = fx+dx, fy+dy
                    if 0 <= nx < W and 0 <= ny < H:
                        dist = max(abs(dx)+abs(dy), 1)
                        self.smoke_map[ny][nx] = min(
                            1.0, self.smoke_map[ny][nx] + 0.35/dist
                        )
        
        # Check for patient failure (fire reached patient)
        fire_set = set(self.fire)
        for p in self.patients:
            if not p.evacuated and p.status != "failed":
                if (p.x, p.y) in fire_set or self.temperature_map[p.y][p.x] > 85:
                    p.status = "failed"
                    self.failed_count += 1
        
        self.update_firefighters() # Run suppression
        self.tick += 1

    # ── Fire spread prediction ─────────────────────────
    def predict_fire_spread(self, ticks_ahead=3):
        """Return cells predicted to be on fire in N ticks (not yet burning)."""
        W, H = self.building.width, self.building.height
        predicted = set(self.fire)
        current   = set(self.fire)
        dirs = [(1,0),(-1,0),(0,1),(0,-1)]
        for _ in range(ticks_ahead):
            nxt = set()
            for fx, fy in current:
                for dx, dy in dirs:
                    nx, ny = fx+dx, fy+dy
                    if 0 <= nx < W and 0 <= ny < H and (nx,ny) not in predicted:
                        nxt.add((nx,ny))
            predicted |= nxt
            current = nxt
        return list(predicted - set(self.fire))

    # ── Firefighter support ───────────────────────────
    def add_firefighter(self, entry_x, entry_y):
        ff = Firefighter(len(self.firefighters), entry_x, entry_y)
        self.firefighters.append(ff)
        return ff

    def get_safe_entry_points(self):
        W, H = self.building.width, self.building.height
        edges = (
            [(x, 0) for x in range(W)] +
            [(x, H-1) for x in range(W)] +
            [(0, y) for y in range(H)] +
            [(W-1, y) for y in range(H)]
        )
        fire_set = set(self.fire)
        return [
            (x, y) for x, y in edges
            if (x,y) not in fire_set and self.smoke_map[y][x] < 0.4
        ]