"""
Data quality validation rules.

Each check function takes a pandas DataFrame (today's data) and returns a
list of issue dicts: {"check": str, "severity": "warning"|"critical", "detail": str}

Add new checks by writing a function and registering it in run_all_checks().
"""

import pandas as pd

import config
import db


def check_null_rates(df: pd.DataFrame):
    issues = []
    for col in df.columns:
        if col in ("order_id", "created_at"):
            continue
        null_rate = df[col].isna().mean()
        if null_rate > config.NULL_RATE_THRESHOLD:
            issues.append({
                "check": "null_rate",
                "severity": "critical" if null_rate > 0.15 else "warning",
                "detail": f"Column '{col}' has {null_rate:.1%} null values "
                          f"(threshold: {config.NULL_RATE_THRESHOLD:.0%})",
            })
    return issues


def check_duplicates(df: pd.DataFrame):
    issues = []
    dup_cols = [c for c in df.columns if c not in ("order_id", "created_at")]
    dup_count = df.duplicated(subset=dup_cols).sum()
    if dup_count > 0:
        issues.append({
            "check": "duplicates",
            "severity": "warning" if dup_count < 10 else "critical",
            "detail": f"Found {dup_count} duplicate row(s) (excluding order_id/created_at)",
        })
    return issues


def check_out_of_range(df: pd.DataFrame):
    issues = []
    for col, (low, high) in config.OUT_OF_RANGE_COLUMNS.items():
        if col not in df.columns:
            continue
        series = df[col].dropna()
        out_of_range = series[(series < low) | (series > high)]
        if len(out_of_range) > 0:
            issues.append({
                "check": "out_of_range",
                "severity": "critical",
                "detail": f"Column '{col}' has {len(out_of_range)} value(s) outside "
                          f"expected range [{low}, {high}] "
                          f"(e.g. {out_of_range.iloc[0]})",
            })
    return issues


def check_row_count_drop(today_df: pd.DataFrame):
    """Compares today's row count against the most recent prior day in the table."""
    issues = []
    conn = db.get_connection()
    rows = conn.execute("""
        SELECT DATE(created_at) as day, COUNT(*) as cnt
        FROM orders
        GROUP BY DATE(created_at)
        ORDER BY day
    """).fetchall()
    conn.close()

    if len(rows) < 2:
        return issues  # not enough history yet

    prev_day, prev_count = rows[-2]["day"], rows[-2]["cnt"]
    today_count = len(today_df)

    if prev_count == 0:
        return issues

    drop_pct = (prev_count - today_count) / prev_count
    if drop_pct > config.ROW_COUNT_DROP_THRESHOLD:
        issues.append({
            "check": "row_count_drop",
            "severity": "critical",
            "detail": f"Row count dropped {drop_pct:.1%} vs previous day "
                      f"({prev_count} -> {today_count})",
        })
    return issues


def run_all_checks(today_df: pd.DataFrame):
    """Runs every registered check and returns a flat list of issues."""
    issues = []
    issues += check_null_rates(today_df)
    issues += check_duplicates(today_df)
    issues += check_out_of_range(today_df)
    issues += check_row_count_drop(today_df)
    return issues


def load_latest_day() -> pd.DataFrame:
    """Loads only the most recent day's rows from the orders table."""
    conn = db.get_connection()
    latest_day = conn.execute("SELECT MAX(DATE(created_at)) FROM orders").fetchone()[0]
    df = pd.read_sql_query(
        "SELECT * FROM orders WHERE DATE(created_at) = ?", conn, params=(latest_day,)
    )
    conn.close()
    return df
