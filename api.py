"""
Trading Signals — FastAPI Backend
Combines: EMA Daily + EMA Weekly + SMA50 Multi-Timeframe Scanner

Endpoints:
  GET  /                         → health check
  GET  /api/health               → health check (JSON)
  GET  /api/symbols              → total symbols loaded
  GET  /api/analyze/{symbol}     → quick single-symbol analysis (all 3 scanners)
  POST /api/scan/start           → start a background scan
  GET  /api/scan/status/{job_id} → poll scan progress
  GET  /api/scan/results/{job_id}→ get full results when done
  GET  /api/jobs                 → list all jobs (history)
"""

import os
import threading
import time
import uuid
from datetime import datetime
from typing import Literal

import pandas as pd
import yfinance as yf
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ─────────────────────────────────────────────────────────────
# APP SETUP
# ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="Trading Signals API",
    description="EMA Daily · EMA Weekly · SMA50 Multi-Timeframe Scanner for S&P500 + Nasdaq-100 + Dow 30",
    version="1.0.0",
)

# Allow any frontend (Lovable, React, etc.) to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store  {job_id: {...}}
jobs: dict = {}

# Latest completed results per scan_type — survives individual job expiry
# {"ema_daily": {...}, "ema_weekly": {...}, "sma50": {...}}
latest_results: dict = {}


# ─────────────────────────────────────────────────────────────
# SHARED UTILITIES
# ─────────────────────────────────────────────────────────────

def load_symbols() -> list[str]:
    try:
        with open("top_indices_symbols.txt", "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []


def calculate_ema(prices: pd.Series, period: int) -> pd.Series | None:
    if len(prices) < period:
        return None
    return prices.ewm(span=period, adjust=False).mean()


def calculate_sma(prices: pd.Series, period: int = 50) -> pd.Series | None:
    if len(prices) < period:
        return None
    return prices.rolling(window=period).mean()


def fetch_history(symbol: str, period: str, interval: str, max_retries: int = 3) -> pd.DataFrame:
    """
    Fetch yfinance history with retry + exponential backoff.
    Retries on empty results to handle transient Yahoo Finance rate limits.
    """
    for attempt in range(max_retries):
        try:
            df = yf.Ticker(symbol).history(period=period, interval=interval)
            if not df.empty:
                return df
            # Empty response — wait and retry
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 1s, 2s, 4s
        except Exception:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    return pd.DataFrame()  # Return empty after all retries exhausted


# ─────────────────────────────────────────────────────────────
# SCANNER 1 — EMA DAILY  (Crossover: fresh break above EMA10)
# ─────────────────────────────────────────────────────────────

def analyze_ema_daily(symbol: str) -> dict | None:
    try:
        df = fetch_history(symbol, period="6mo", interval="1d")
        if df.empty or len(df) < 41:
            return None

        df["EMA10"] = calculate_ema(df["Close"], 10)
        df["EMA20"] = calculate_ema(df["Close"], 20)
        df["EMA40"] = calculate_ema(df["Close"], 40)
        df = df.dropna(subset=["EMA10", "EMA20", "EMA40"])
        if len(df) < 2:
            return None

        # Today
        row   = df.iloc[-1]
        price = round(float(row["Close"]), 2)
        ema10 = round(float(row["EMA10"]), 2)
        ema20 = round(float(row["EMA20"]), 2)
        ema40 = round(float(row["EMA40"]), 2)

        # Previous day
        prev = df.iloc[-2]
        prev_close = float(prev["Close"])
        prev_ema10 = float(prev["EMA10"])

        # 6 crossover conditions
        c1 = price > ema10            # Close > EMA10
        c2 = price > ema20            # Close > EMA20
        c3 = price > ema40            # Close > EMA40
        c4 = prev_close < prev_ema10  # Prev Close < Prev EMA10
        c5 = ema20 > ema40            # EMA20 > EMA40
        c6 = ema10 > ema20            # EMA10 > EMA20

        if c1 and c2 and c3 and c4 and c5 and c6:
            return {
                "symbol":    symbol,
                "signal":    "BULLISH",
                "timeframe": "daily",
                "price":     price,
                "ema10":     ema10,
                "ema20":     ema20,
                "ema40":     ema40,
                "condition": "Fresh crossover above EMA10 · EMAs stacked bullish",
            }
        return None
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────
# SCANNER 2 — EMA WEEKLY  (Crossover: fresh break above EMA10)
# ─────────────────────────────────────────────────────────────

def analyze_ema_weekly(symbol: str) -> dict | None:
    try:
        df = fetch_history(symbol, period="2y", interval="1wk")
        if df.empty or len(df) < 41:
            return None

        df["EMA10"] = calculate_ema(df["Close"], 10)
        df["EMA20"] = calculate_ema(df["Close"], 20)
        df["EMA40"] = calculate_ema(df["Close"], 40)
        df = df.dropna(subset=["EMA10", "EMA20", "EMA40"])
        if len(df) < 2:
            return None

        # This week
        row   = df.iloc[-1]
        price = round(float(row["Close"]), 2)
        ema10 = round(float(row["EMA10"]), 2)
        ema20 = round(float(row["EMA20"]), 2)
        ema40 = round(float(row["EMA40"]), 2)

        # Previous week
        prev = df.iloc[-2]
        prev_close = float(prev["Close"])
        prev_ema10 = float(prev["EMA10"])

        # 6 crossover conditions
        c1 = price > ema10            # Close > EMA10
        c2 = price > ema20            # Close > EMA20
        c3 = price > ema40            # Close > EMA40
        c4 = prev_close < prev_ema10  # Prev Close < Prev EMA10
        c5 = ema20 > ema40            # EMA20 > EMA40
        c6 = ema10 > ema20            # EMA10 > EMA20

        if c1 and c2 and c3 and c4 and c5 and c6:
            return {
                "symbol":    symbol,
                "signal":    "BULLISH",
                "timeframe": "weekly",
                "price":     price,
                "ema10":     ema10,
                "ema20":     ema20,
                "ema40":     ema40,
                "condition": "Fresh crossover above EMA10 · EMAs stacked bullish",
            }
        return None
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────
# SCANNER 3 — SMA50  (Above SMA50 on Daily + 1HR + 15min)
# ─────────────────────────────────────────────────────────────

def _get_sma_position(symbol: str, interval: str) -> tuple:
    """Returns (position, price, sma50) for the given interval."""
    try:
        periods = {"1d": "3mo", "1h": "1mo", "15m": "5d"}
        if interval not in periods:
            return None, None, None

        df = fetch_history(symbol, period=periods[interval], interval=interval)
        if df.empty or len(df) < 51:
            return None, None, None

        df["SMA50"] = calculate_sma(df["Close"], 50)
        df = df.dropna(subset=["SMA50"])
        if df.empty:
            return None, None, None

        row      = df.iloc[-1]
        price    = round(float(row["Close"]), 2)
        sma      = round(float(row["SMA50"]), 2)
        position = "above" if price > sma else "below"
        return position, price, sma
    except Exception:
        return None, None, None


def analyze_sma50(symbol: str) -> dict | None:
    try:
        d_pos,  d_price,  d_sma  = _get_sma_position(symbol, "1d")
        h_pos,  h_price,  h_sma  = _get_sma_position(symbol, "1h")
        m_pos,  m_price,  m_sma  = _get_sma_position(symbol, "15m")

        if None in [d_pos, h_pos, m_pos]:
            return None

        if d_pos == "above" and h_pos == "above" and m_pos == "above":
            return {
                "symbol":        symbol,
                "signal":        "BULLISH",
                "timeframe":     "daily+1h+15m",
                "daily_price":   d_price,
                "daily_sma50":   d_sma,
                "hourly_price":  h_price,
                "hourly_sma50":  h_sma,
                "min15_price":   m_price,
                "min15_sma50":   m_sma,
                "condition":     "Price above SMA50 on Daily + 1HR + 15min",
            }
        return None
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────
# BACKGROUND SCAN RUNNER
# ─────────────────────────────────────────────────────────────

SCAN_CONFIG = {
    "ema_daily":  {"fn": analyze_ema_daily,  "delay": 0.5, "label": "EMA Daily"},
    "ema_weekly": {"fn": analyze_ema_weekly, "delay": 0.5, "label": "EMA Weekly"},
    "sma50":      {"fn": analyze_sma50,      "delay": 1.0, "label": "SMA50 Multi-TF"},
}  # Larger delays prevent Yahoo Finance rate limiting on server IPs


def _run_scan(job_id: str, scan_type: str) -> None:
    symbols = load_symbols()
    if not symbols:
        jobs[job_id].update({"status": "failed", "error": "top_indices_symbols.txt not found"})
        return

    cfg     = SCAN_CONFIG[scan_type]
    total   = len(symbols)
    results = []

    jobs[job_id].update({"status": "running", "total": total, "progress": 0})

    for i, symbol in enumerate(symbols, 1):
        result = cfg["fn"](symbol)
        if result:
            results.append(result)

        jobs[job_id]["progress"] = i
        jobs[job_id]["results"]  = results  # live update so frontend can peek
        time.sleep(cfg["delay"])

    completed_payload = {
        "status":        "completed",
        "completed_at":  datetime.now().isoformat(),
        "results":       results,
    }
    jobs[job_id].update(completed_payload)

    # Also persist as latest for this scan type — survives job dict expiry
    latest_results[scan_type] = {
        "scan_type":     scan_type,
        "label":         cfg["label"],
        "completed_at":  completed_payload["completed_at"],
        "total_scanned": total,
        "results_count": len(results),
        "results":       results,
    }


# ─────────────────────────────────────────────────────────────
# REQUEST / RESPONSE MODELS
# ─────────────────────────────────────────────────────────────

class ScanRequest(BaseModel):
    type: Literal["ema_daily", "ema_weekly", "sma50"]


# ─────────────────────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
@app.head("/", tags=["Health"])
def root():
    return {
        "status":    "ok",
        "message":   "Trading Signals API is running 🚀",
        "timestamp": datetime.now().isoformat(),
        "docs":      "/docs",
    }


@app.get("/api/health", tags=["Health"])
def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.get("/api/symbols", tags=["Info"])
def get_symbols():
    symbols = load_symbols()
    return {"count": len(symbols), "symbols": symbols}


@app.get("/api/analyze/{symbol}", tags=["Quick Analysis"])
def analyze_symbol(symbol: str):
    """
    Run all 3 scanners on a single symbol instantly.
    Great for testing from the frontend.
    """
    sym = symbol.upper()
    return {
        "symbol":    sym,
        "timestamp": datetime.now().isoformat(),
        "ema_daily":  analyze_ema_daily(sym),
        "ema_weekly": analyze_ema_weekly(sym),
        "sma50":      analyze_sma50(sym),
    }


@app.post("/api/scan/start", tags=["Scan"])
def start_scan(body: ScanRequest):
    """
    Start a background scan. Returns a job_id.
    Poll /api/scan/status/{job_id} to track progress.
    """
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "job_id":     job_id,
        "scan_type":  body.type,
        "label":      SCAN_CONFIG[body.type]["label"],
        "status":     "queued",
        "progress":   0,
        "total":      0,
        "results":    [],
        "started_at": datetime.now().isoformat(),
        "completed_at": None,
    }

    thread = threading.Thread(target=_run_scan, args=(job_id, body.type), daemon=True)
    thread.start()

    return {
        "job_id":    job_id,
        "scan_type": body.type,
        "status":    "queued",
        "message":   f"Scan started. Poll /api/scan/status/{job_id} for live progress.",
    }


@app.get("/api/scan/status/{job_id}", tags=["Scan"])
def scan_status(job_id: str):
    """Poll this to track progress. When status=completed, results are included directly."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    pct = round((job["progress"] / job["total"]) * 100, 1) if job["total"] else 0
    is_done = job["status"] == "completed"

    response = {
        "job_id":         job_id,
        "scan_type":      job.get("scan_type"),
        "label":          job.get("label"),
        "status":         job["status"],
        "progress":       job["progress"],
        "total":          job["total"],
        "percent":        pct,
        "results_so_far": len(job["results"]),
        "results_count":  len(job["results"]),
        "started_at":     job.get("started_at"),
        "completed_at":   job.get("completed_at"),
        # Always include results so frontend never needs a second call
        "results":        job["results"],
    }
    return response


@app.get("/api/scan/results/{job_id}", tags=["Scan"])
def scan_results(job_id: str):
    """Get the full results of a scan (available even while still running)."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    return {
        "job_id":        job_id,
        "scan_type":     job.get("scan_type"),
        "label":         job.get("label"),
        "status":        job["status"],
        "total_scanned": job["progress"],
        "results_count": len(job["results"]),
        "results":       job["results"],
        "started_at":    job.get("started_at"),
        "completed_at":  job.get("completed_at"),
    }


@app.get("/api/scan/latest/{scan_type}", tags=["Scan"])
def latest_scan_results(scan_type: str):
    """
    Returns the most recent COMPLETED results for a scan type.
    Use this as a fallback if job_id is lost or the instance restarted.
    scan_type must be: ema_daily | ema_weekly | sma50
    """
    if scan_type not in SCAN_CONFIG:
        raise HTTPException(status_code=400, detail=f"Unknown scan_type. Use: {list(SCAN_CONFIG.keys())}")
    if scan_type not in latest_results:
        raise HTTPException(status_code=404, detail="No completed scan found for this type yet. Run a scan first.")
    return latest_results[scan_type]


@app.get("/api/jobs", tags=["Scan"])
def list_jobs():
    """List all scan jobs (history for this session)."""
    summary = []
    for jid, job in jobs.items():
        pct = round((job["progress"] / job["total"]) * 100, 1) if job["total"] else 0
        summary.append({
            "job_id":        jid,
            "scan_type":     job.get("scan_type"),
            "label":         job.get("label"),
            "status":        job["status"],
            "percent":       pct,
            "results_count": len(job["results"]),
            "started_at":    job.get("started_at"),
            "completed_at":  job.get("completed_at"),
        })
    return {"jobs": sorted(summary, key=lambda x: x["started_at"] or "", reverse=True)}


# ─────────────────────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=False)
