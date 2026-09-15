"""
Simulates a daily orders feed landing in the database.

In a real deployment this table would be populated by an upstream system
(an application DB, an ETL job, a CSV drop, etc). This script exists so
the pipeline is runnable and demoable end-to-end without external
dependencies — run it once per "day" to simulate new data arriving.

Usage:
    python src/generate_data.py --day 1   # clean baseline day
    python src/generate_data.py --day 2   # day with injected data quality issues
"""

import argparse
import random
from datetime import datetime, timedelta

import db


def generate_rows(day: int, inject_issues: bool):
    """Generate a batch of synthetic order rows for a given simulated day."""
    rows = []
    base_date = datetime(2026, 9, 10) + timedelta(days=day - 1)
    row_count = 200 if not inject_issues else 120  # simulate a volume drop on bad days

    regions = ["South", "North", "East", "West"]

    for i in range(row_count):
        amount = round(random.uniform(50, 5000), 2)
        quantity = random.randint(1, 20)
        customer_id = random.randint(1000, 1999)
        region = random.choice(regions)

        if inject_issues:
            roll = random.random()
            if roll < 0.08:
                amount = None                       # null amount
            elif roll < 0.14:
                amount = -250.0                      # negative / out-of-range amount
            elif roll < 0.18:
                quantity = 9999                       # absurd quantity, out of range
            elif roll < 0.22:
                customer_id = None                    # null customer_id

        rows.append((
            customer_id, amount, quantity, region,
            (base_date + timedelta(minutes=i)).isoformat(),
        ))

    # Inject a handful of exact-duplicate rows on "bad" days
    if inject_issues and rows:
        dup = rows[0]
        rows.extend([dup] * 6)

    return rows


def insert_rows(rows):
    conn = db.get_connection()
    conn.executemany("""
        INSERT INTO orders (customer_id, amount, quantity, region, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, rows)
    conn.commit()
    conn.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--day", type=int, default=1, help="Simulated day number")
    parser.add_argument("--clean", action="store_true", help="Force a clean day (no injected issues)")
    args = parser.parse_args()

    db.init_schema()

    inject_issues = (args.day > 1) and not args.clean
    rows = generate_rows(args.day, inject_issues)
    insert_rows(rows)

    print(f"[generate_data] Day {args.day}: inserted {len(rows)} rows "
          f"({'with injected issues' if inject_issues else 'clean'}).")


if __name__ == "__main__":
    main()
