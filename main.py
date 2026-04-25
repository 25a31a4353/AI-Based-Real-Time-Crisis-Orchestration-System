import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

# Simulation imports (keep your existing logic)
from simulation.simulation_engine import Simulation, Building, Patient, Staff

app = FastAPI()

# Enable CORS so the browser doesn't block requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DIRECTORY PATHING ---
# This finds the exact folder where main.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# --- ROUTES ---

# 1. Serves the main page
@app.get("/")
async def read_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": f"index.html not found at {index_path}. Check your static folder!"}

# 2. Serves CSS/JS files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 3. Your simulation API
@app.post("/api/tick")
async def simulate_tick():
    # Your Antigravity logic here
    return {"status": "success", "message": "Tick processed"}