from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="ATLAS Orchestration", version="1.0.0")


@app.get("/health")
async def health():
    return {"status": "operational", "service": "atlas-orchestration", "timestamp": datetime.utcnow().isoformat()}


@app.post("/workflow/start")
async def start_workflow(lead: dict):
    return {"status": "started", "lead_id": lead.get("lead_id"), "next": "enrich"}
