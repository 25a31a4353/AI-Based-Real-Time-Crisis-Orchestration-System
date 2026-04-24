import urllib.request, json

BASE = "http://localhost:8090"

def get(path):
    with urllib.request.urlopen(BASE + path, timeout=10) as r:
        return json.loads(r.read())

def post(path, data=b"{}"):
    req = urllib.request.Request(
        BASE + path, data=data, method="POST",
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

print("=== GET /health ===")
h = get("/health")
print(f"  status={h['status']}  tick={h['tick']}")

print("\n=== POST /api/tick  (x3) ===")
for i in range(3):
    t = post("/api/tick")
    print(f"  tick={t['tick']}  fire={t['fire_cells']}  assigned={t['assignments']}")

print("\n=== GET /api/safe-routes ===")
sr = get("/api/safe-routes")
print(f"  count={sr['count']}")
for r in sr["routes"]:
    print(f"    {r['route_id']}  risk={r['risk_level']}  warning={r['warning']}")

print("\n=== GET /api/hazard-alerts ===")
ha = get("/api/hazard-alerts")
by_type = {}
for a in ha["alerts"]:
    by_type[a["type"]] = by_type.get(a["type"], 0) + 1
print(f"  total alerts={ha['count']}")
for k, v in by_type.items():
    print(f"    {k}: {v}")

print("\n=== GET /api/dashboard ===")
db = get("/api/dashboard")
s = db["stats"]
print(f"  tick={db['tick']}  fire_cells={s['fire_cells']}")
print(f"  assignments={s['assignments']}  completed={s['completed']}  failed={s['failed']}")
print(f"  top_patient={s['top_patient']}  top_score={s['top_score']}")
direction = db.get("ai_fire_direction", "")[:70]
print(f"  ai_direction={direction}...")

print("\n=== ALL ENDPOINTS VERIFIED — No errors. ===")
