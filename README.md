# 📈 Trading Signals Dashboard

A full-stack stock scanner that detects **EMA crossover signals** and **SMA50 multi-timeframe setups** across 500+ US stocks (S&P 500, Nasdaq-100, Dow 30).

- **Backend** — Python + FastAPI (runs on port 8000)
- **Frontend** — React + Vite (runs on port 3000)

---

## ⚙️ Prerequisites

Make sure you have these installed before starting:

| Tool | Version | Check command |
|------|---------|---------------|
| Python | 3.10 or newer | `python3 --version` |
| Node.js | 18 or newer | `node --version` |
| npm | 8 or newer | `npm --version` |

> **Don't have Python?** Download from https://www.python.org/downloads/  
> **Don't have Node.js?** Download from https://nodejs.org (pick the LTS version)

---

## 🚀 Setup — Step by Step

### Step 1 — Clone the repo

Open your Terminal (Mac) or Command Prompt (Windows) and run:

```bash
git clone https://github.com/Shaam03/trading-signals-api.git
cd trading-signals-api
```

---

### Step 2 — Set up the Python backend

**Create a virtual environment** (keeps Python packages isolated):

```bash
# Mac / Linux
python3 -m venv .venv

# Windows
python -m venv .venv
```

**Activate the virtual environment:**

```bash
# Mac / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

> ✅ You'll know it's active when you see `(.venv)` at the start of your terminal line.

**Install Python packages:**

```bash
pip install -r requirements.txt
```

---

### Step 3 — Set up the React frontend

```bash
cd frontend
npm install
cd ..
```

> This installs all the frontend dependencies listed in `frontend/package.json`.

---

### Step 4 — Run the app

You need **two terminals open at the same time**.

**Terminal 1 — Start the backend:**

```bash
# Make sure you're in the root project folder (trading-signals-api)
# Make sure the venv is activated — you'll see (.venv) in your prompt

source .venv/bin/activate   # Mac/Linux  (skip if already active)
.venv\Scripts\activate      # Windows    (skip if already active)

python api.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Terminal 2 — Start the frontend:**

```bash
cd frontend
npm run dev
```

You should see:
```
VITE v7.x.x  ready in xxx ms
➜  Local:   http://localhost:3000/
```

---

### Step 5 — Open the dashboard

Go to **http://localhost:3000** in your browser. 🎉

The green dot in the top-right of the navbar means the backend is connected and ready.

---

## 🔍 How to Use

### Quick Symbol Lookup
Type any stock ticker (e.g. `AAPL`, `NVDA`, `TSLA`) in the search bar and press Enter.  
It will instantly show you the EMA Daily, EMA Weekly, and SMA50 signals for that stock.

### Full Market Scan
Click **Start Scan** on any of the 3 scanner cards:
- **EMA Daily** — scans all 500+ stocks on the daily chart
- **EMA Weekly** — scans all 500+ stocks on the weekly chart
- **SMA50 Multi-TF** — scans all 500+ stocks across Daily, 1HR, and 15min

A progress bar shows live progress. When done, the results appear in a table below where you can filter, sort, and export to CSV.

> ⏱ Full scans take ~5–10 minutes due to Yahoo Finance rate limits.

---

## 📊 Signal Logic

### EMA Daily & Weekly (6 conditions — all must be true)

| # | Condition | What it means |
|---|-----------|---------------|
| 1 | Close > EMA10 | Price above fast EMA |
| 2 | Close > EMA20 | Price above mid EMA |
| 3 | Close > EMA40 | Price above slow EMA |
| 4 | **Prev Close < Prev EMA10** | Price was below EMA10 last bar → **fresh crossover** |
| 5 | EMA20 > EMA40 | Mid trend stacked above slow |
| 6 | EMA10 > EMA20 | Fast trend stacked above mid |

### SMA50 Multi-Timeframe
Price must be **above SMA50** on all 3 timeframes simultaneously:
- Daily chart
- 1-Hour chart
- 15-Minute chart

---

## 🛑 Stopping the app

Press `Ctrl + C` in each terminal to stop the backend and frontend.

---

## ❓ Troubleshooting

**`python3: command not found`**  
→ Use `python` instead of `python3` (Windows)

**`npm: command not found`**  
→ Node.js is not installed. Download from https://nodejs.org

**Backend shows no results / 0 stocks found**  
→ Yahoo Finance may be rate-limiting. Wait a few minutes and try again.

**Frontend shows red dot (API offline)**  
→ Make sure the backend (`python api.py`) is running in another terminal.

**Port already in use**  
→ Something else is using port 8000 or 3000. Restart your terminal and try again.
