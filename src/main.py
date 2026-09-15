"""
Main entry point — orchestrates one full pipeline run:
load latest data -> run checks -> send alerts -> write report.

Usage:
    python src/main.py --day 1
    python src/main.py --day 2

Typically scheduled via cron, e.g. to run every day at 7am:
    0 7 * * * /usr/bin/python3 /path/to/src/main.py >> logs/cron.log 2>&1
"""

import argparse

import alerts
import report
import validators


def run_pipeline(day_label: str):
    today_df = validators.load_latest_day()
    if today_df.empty:
        print("[main] No data found for the latest day — nothing to check.")
        return None

    issues = validators.run_all_checks(today_df)
    alerts.send_alerts(issues)
    rep = report.generate_report(day_label, len(today_df), issues)

    print(f"[main] Pipeline run complete. Status: {rep['status']}")
    return rep


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--day", type=str, default="latest", help="Label for this run's report filename")
    args = parser.parse_args()
    run_pipeline(args.day)
