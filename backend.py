"""
SolarCheck — minimal backend
Collects survey responses (POST) and serves them to the dashboard (GET).
Storage: SQLite (zero setup). Swap to PostgreSQL later if needed.

Run locally:
    pip install fastapi uvicorn
    uvicorn backend:app --reload --port 8000

Endpoints:
    POST /responses   <- survey ka SUBMIT_ENDPOINT
    GET  /responses   <- dashboard ka DATA_ENDPOINT
"""
import json, sqlite3, datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SolarCheck API")

# CORS: survey/dashboard doosre domain pe honge, isliye khula rakha.
# Production mein allow_origins ko apne domains tak mehdood karo.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

DB = "solarcheck.db"

def db():
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS responses (id INTEGER PRIMARY KEY, data TEXT, created TEXT)")
    return con

@app.post("/responses")
async def add_response(req: Request):
    payload = await req.json()
    con = db()
    con.execute(
        "INSERT INTO responses (data, created) VALUES (?, ?)",
        (json.dumps(payload), datetime.datetime.utcnow().isoformat()),
    )
    con.commit(); con.close()
    return {"ok": True}

@app.get("/responses")
def list_responses():
    con = db()
    rows = con.execute("SELECT data FROM responses ORDER BY id DESC").fetchall()
    con.close()
    # dashboard ek plain JSON array expect karta hai
    return [json.loads(r[0]) for r in rows]

@app.get("/")
def health():
    return {"status": "SolarCheck API live"}
