"""
FastAPI service exposing the data quality pipeline.

Run with:
    uvicorn src.api:app --reload --port 8000

Endpoints:
    GET  /report/latest   -> most recent report (JSON)
    GET  /reports         -> list all historical report filenames
    POST /run             -> trigger a fresh pipeline run and return its report
"""

import json
import os

from fastapi import FastAPI, HTTPException

import config
import main as pipeline

app = FastAPI(
    title="Data Quality Monitoring API",
    description="Serves data quality check results for the orders pipeline.",
    version="1.0.0",
)


@app.get("/report/latest")
def get_latest_report():
    path = os.path.join(config.REPORTS_DIR, "latest.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="No reports generated yet. POST /run first.")
    with open(path) as f:
        return json.load(f)


@app.get("/reports")
def list_reports():
    if not os.path.exists(config.REPORTS_DIR):
        return {"reports": []}
    files = sorted(f for f in os.listdir(config.REPORTS_DIR) if f.endswith(".json") and f != "latest.json")
    return {"reports": files}


@app.post("/run")
def trigger_run():
    rep = pipeline.run_pipeline("on_demand")
    if rep is None:
        raise HTTPException(status_code=400, detail="No data available to check.")
    return rep


@app.get("/health")
def health():
    return {"status": "ok"}
