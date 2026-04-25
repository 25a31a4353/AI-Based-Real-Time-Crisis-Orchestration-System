import random

class Patient:
    def __init__(self, pid, x, y, floor=0, movable=True, condition="stable"):
        self.id        = pid
        self.x         = x
        self.y         = y
        self.floor     = floor
        self.movable   = movable
        self.condition = condition
        self.evacuated = False

class Staff:
    def __init__(self, sid, x, y, floor=0, trained=True, role="medic"):
        self.id      = sid
        self.x       = x
        self.y       = y
        self.floor   = floor
        self.trained = trained
        self.role    = role
        self.load    = 0

class Firefighter:
    def __init__(self, fid, x, y):
        self.id            = fid
        self.x             = x
        self.y             = y
        self.assigned_zone = None

class Building:
    def __init__(self, width=10, height=10, floors=1):
        self.width  = width
        self.height = height
        self.floors = floors
        self.exits  = [
            (0,0),(width-1,0),(0,height-1),(width-1,height-1),
            (width//2,0),(width//2,height-1)
        ]

class Simulation:
    def __init__(self, building, patients, staff, fire_origin=None, fire_speed=1):
        self.building     = building
        self.patients     = patients
        self.staff        = staff
        self.firefighters = []
        self.fire_speed   = fire_speed
        self.grids = [
            [["." for _ in range(building.width)] for _ in range(building.height)]
            for _ in range(building.floors)
        ]
        self.temperature_map = [
            [[20.0]*building.width for _ in range(building.height)]
            for _ in range(building.floors)
        ]
        self.smoke_map = [
            [[0.0]*building.width for _ in range(building.height)]
            for _ in range(building.floors)
        ]
        self.fire          = []
        self.fire_severity = {}
        self.tick          = 0
        if fire_origin:
            fx, fy, ff = fire_origin
        else:
            fx = building.width // 2
            fy = building.height // 2
            ff = 0
        self._start_fire(fx, fy, ff)
        self._place_entities()

    def _start_fire(self, x, y, floor):
        origin = (x, y, floor)
        self.fire.append(origin)
        self.fire_severity[origin] = 4
        self.grids[floor][y][x] = "F"
        self.temperature_map[floor][y][x] = 95.0

    def _place_entities(self):
        for p in self.patients:
            f = min(p.floor, self.building.floors-1)
            self.grids[f][p.y][p.x] = "P"
        for s in self.staff:
            f = min(s.floor, self.building.floors-1)
            self.grids[f][s.y][s.x] = "S"

    def update_fire(self):
        W, H = self.building.width, self.building.height
        cardinal = [(1,0),(-1,0),(0,1),(0,-1)]
        diagonal = [(1,1),(-1,1),(1,-1),(-1,-1)]
        for _ in range(self.fire_speed):
            new_fire = []
            for fx, fy, ff in self.fire:
                sev  = self.fire_severity.get((fx,fy,ff), 2)
                dirs = cardinal if sev < 3 else cardinal + diagonal
                for dx, dy in dirs:
                    nx, ny = fx+dx, fy+dy
                    if 0 <= nx < W and 0 <= ny < H and (nx,ny,ff) not in self.fire_severity:
                        new_fire.append((nx, ny, ff, max(1, sev-1)))
            for nx, ny, nf, sev in new_fire:
                self.fire.append((nx, ny, nf))
                self.fire_severity[(nx,ny,nf)] = sev
                self.grids[nf][ny][nx] = "F"
                self.temperature_map[nf][ny][nx] = min(100, self.temperature_map[nf][ny][nx]+40)
        for fx, fy, ff in self.fire:
            sev = self.fire_severity.get((fx,fy,ff), 1)
            for dx in range(-2,3):
                for dy in range(-2,3):
                    nx, ny = fx+dx, fy+dy
                    if 0 <= nx < W and 0 <= ny < H:
                        dist = max(abs(dx)+abs(dy), 1)
                        self.temperature_map[ff][ny][nx] = min(100,
                            self.temperature_map[ff][ny][nx]+(sev*12)/dist)
        for fx, fy, ff in self.fire:
            for dx in range(-3,4):
                for dy in range(-3,5):
                    nx, ny = fx+dx, fy+dy
                    if 0 <= nx < W and 0 <= ny < H:
                        dist = max(abs(dx)+abs(dy), 1)
                        self.smoke_map[ff][ny][nx] = min(1.0,
                            self.smoke_map[ff][ny][nx]+0.35/dist)
        self.tick += 1

    def predict_fire_spread(self, ticks_ahead=3):
        W, H = self.building.width, self.building.height
        predicted = set((x,y,f) for x,y,f in self.fire)
        current   = set(predicted)
        dirs = [(1,0),(-1,0),(0,1),(0,-1)]
        for _ in range(ticks_ahead):
            nxt = set()
            for fx, fy, ff in current:
                for dx, dy in dirs:
                    nx, ny = fx+dx, fy+dy
                    if 0 <= nx < W and 0 <= ny < H and (nx,ny,ff) not in predicted:
                        nxt.add((nx,ny,ff))
            predicted |= nxt
            current = nxt
        return list(predicted - set((x,y,f) for x,y,f in self.fire))

    def add_firefighter(self, x, y, floor=0):
        ff = Firefighter(len(self.firefighters), x, y)
        self.firefighters.append(ff)
        return ff

    def get_safe_entry_points(self, floor=0):
        W, H = self.building.width, self.building.height
        edges = (
            [(x,0,floor) for x in range(W)] +
            [(x,H-1,floor) for x in range(W)] +
            [(0,y,floor) for y in range(H)] +
            [(W-1,y,floor) for y in range(H)]
        )
        fire_set = set((x,y,f) for x,y,f in self.fire)
        return [(x,y,f) for x,y,f in edges
                if (x,y,f) not in fire_set and self.smoke_map[f][y][x] < 0.4]


def build_from_params(width, height, floors, num_patients, num_icu,
                      num_staff, num_trained, fire_x, fire_y, fire_floor, fire_speed):
    building = Building(width, height, floors)
    random.seed(42)
    W, H = width, height
    occupied = set()
    fire_pos = (fire_x, fire_y)

    def rand_pos(fl):
        for _ in range(200):
            x = random.randint(1, W-2)
            y = random.randint(1, H-2)
            if (x,y,fl) not in occupied and (x,y) != fire_pos:
                occupied.add((x,y,fl))
                return x, y
        return 1, 1

    patients = []
    for i in range(num_patients):
        fl = random.randint(0, floors-1)
        x, y = rand_pos(fl)
        is_icu = (i < num_icu)
        patients.append(Patient(i, x, y, floor=fl, movable=not is_icu,
                                condition="critical" if is_icu else "stable"))
    staff = []
    for i in range(num_staff):
        fl = random.randint(0, floors-1)
        x, y = rand_pos(fl)
        trained = (i < num_trained)
        staff.append(Staff(i, x, y, floor=fl, trained=trained,
                           role="medic" if trained else "nurse"))

    fire_fl = min(fire_floor, floors-1)
    return Simulation(building, patients, staff,
                      fire_origin=(fire_x, fire_y, fire_fl),
                      fire_speed=fire_speed)
