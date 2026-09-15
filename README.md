# Automated Data Quality Monitoring Pipeline

A Python pipeline that validates incoming data against configurable rules, sends real-time alerts when problems are found, and generates daily summary reports — with an optional REST API for on-demand checks.

Built to simulate a real-world scenario: a daily `orders` feed lands in a database, and this pipeline automatically checks it for the kinds of problems that quietly break downstream reports (missing values, duplicates, out-of-range numbers, sudden volume drops) before anyone notices manually.

## Why this project

Manual data quality checks don't scale and are easy to skip under deadline pressure. This pipeline automates the checks, alerts the right people immediately when something's wrong, and keeps a historical record — the same pattern used in production ETL/data engineering systems, scaled down to something you can run and understand end-to-end in a weekend.

## Features

- **Configurable validation rules**: null-rate thresholds, duplicate detection, out-of-range values, day-over-day row count drops
- **Alerting**: Slack webhook and/or email, with automatic local file logging as a fallback (so it works with zero external accounts configured)
- **Reporting**: JSON + Markdown daily summary reports, written to `reports/`
- **REST API** (optional): FastAPI endpoints to fetch the latest report or trigger a run on demand
- **Zero-dependency core**: the validation pipeline runs on Python's built-in `sqlite3` — no database server required to try it out
- **MySQL-ready**: swap one config value to point the pipeline at a real MySQL database
- **Tested**: unit tests covering every validation rule (`pytest tests/`)

## Architecture

```
                 ┌─────────────────┐
   generate_data │   orders table   │
   .py (or a     │  (SQLite/MySQL)  │
   real upstream │                  │
   system) ─────▶│                  │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  validators.py   │  null rates, duplicates,
                 │  (check engine)  │  out-of-range, volume drop
                 └────────┬─────────┘
                          │ issues[]
              ┌───────────┼────────────┐
              ▼           ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │alerts.py │ │report.py │ │  api.py   │
        │Slack/    │ │ JSON +   │ │ FastAPI   │
        │email/log │ │ Markdown │ │ endpoints │
        └──────────┘ └──────────┘ └──────────┘
```

## Project structure

```
data-quality-monitor/
├── src/
│   ├── config.py          # thresholds, paths, env-driven settings
│   ├── db.py               # sqlite3 connection + schema
│   ├── generate_data.py    # simulates a daily orders feed (demo/testing only)
│   ├── validators.py       # the actual data quality checks
│   ├── alerts.py            # Slack/email/local-log alerting
│   ├── report.py            # JSON + Markdown report generation
│   ├── main.py               # orchestrates one full pipeline run
│   └── api.py                 # optional FastAPI serving layer
├── tests/
│   └── test_validators.py     # unit tests for every check
├── data/                        # sqlite db lives here (gitignored)
├── reports/                      # generated reports land here
├── logs/                          # local alert log (gitignored)
├── requirements.txt
├── .env.example
└── README.md
```

## Quickstart

```bash
git clone <your-repo-url>
cd data-quality-monitor
pip install -r requirements.txt

# Simulate day 1 (clean data) and run the pipeline
python src/generate_data.py --day 1
python src/main.py --day day1

# Simulate day 2 (realistic data problems) and run again
python src/generate_data.py --day 2
python src/main.py --day day2

# Check the reports
cat reports/report_day2.md
```

### Sample output (Day 2 — problem data)

```
[alerts]
Data Quality Alert — 6 issue(s) found (3 critical, 3 warning)
  [WARNING] null_rate: Column 'customer_id' has 7.1% null values (threshold: 5%)
  [WARNING] null_rate: Column 'amount' has 10.3% null values (threshold: 5%)
  [WARNING] duplicates: Found 6 duplicate row(s) (excluding order_id/created_at)
  [CRITICAL] out_of_range: Column 'amount' has 5 value(s) outside expected range [0, 100000]
  [CRITICAL] out_of_range: Column 'quantity' has 4 value(s) outside expected range [1, 500]
  [CRITICAL] row_count_drop: Row count dropped 37.0% vs previous day (200 -> 126)
[main] Pipeline run complete. Status: FAIL
```

### Running the API

```bash
uvicorn src.api:app --reload --port 8000
# then visit http://localhost:8000/docs for interactive Swagger UI
```

- `GET /report/latest` — most recent report as JSON
- `GET /reports` — list all historical reports
- `POST /run` — trigger a fresh pipeline run

### Running tests

```bash
pytest tests/ -v
```

## Switching to MySQL

The core pipeline (`db.py`) uses SQLite for zero-setup local development. To run against MySQL instead for the API/SQLAlchemy layer:

```bash
export DB_URL="mysql+pymysql://user:password@localhost:3306/orders_db"
```

## Scheduling (automation)

Run the pipeline automatically every morning with cron:

```
0 7 * * * cd /path/to/data-quality-monitor && /usr/bin/python3 src/main.py >> logs/cron.log 2>&1
```

## Enabling real alerts

Copy `.env.example` to `.env` and fill in a Slack webhook URL and/or SMTP credentials. Without these set, alerts are still fully logged to `logs/alerts.log` and printed to console — the pipeline degrades gracefully rather than failing silently.

## Tech stack

Python · pandas · SQLite/MySQL · FastAPI · Slack webhooks · pytest

## License

MIT
