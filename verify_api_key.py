import os
os.environ["GOOGLE_API_KEY"] = "AIzaSyB1Fn1aFSFkiSVq3Msj0IWIEKCvytu8chw"

from fastapi.testclient import TestClient
from api.main import app
import json

client = TestClient(app)

print("--- Resetting Simulation ---")
client.post("/api/reset")

print("\n--- Sending request to advance simulation (/api/tick) ---")
resp_tick = client.post("/api/tick")
tick_data = resp_tick.json()

print(f"Survival Probability (Rate): {tick_data.get('success_stats', {}).get('survival_rate')}")
print(f"AI Fire Direction reasoning: {tick_data.get('ai_fire_direction')}")

print("\n--- Fetching Dashboard data to check Priority Score ---")
resp_dash = client.get("/api/dashboard")
dash_data = resp_dash.json()

print(f"Top Priority Score: {dash_data.get('stats', {}).get('top_score')}")

if "[Gemma unavailable" in str(tick_data.get('ai_fire_direction')):
    print("\n[!] ERROR: The AI client failed to authenticate or connect.")
else:
    print("\n[+] SUCCESS: The GOOGLE_API_KEY was successfully read by the AI client.")
