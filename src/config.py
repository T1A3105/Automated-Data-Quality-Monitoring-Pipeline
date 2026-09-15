"""
Central configuration for the Data Quality Monitoring Pipeline.

DB_URL defaults to a local SQLite file so the project runs out-of-the-box
with zero setup. To point it at MySQL instead, set the DB_URL environment
variable, e.g.:

    export DB_URL="mysql+pymysql://user:password@localhost:3306/orders_db"

No other code needs to change — SQLAlchemy handles both backends.
"""

import os

# Resolve all paths relative to the project root (parent of src/) so the
# pipeline works the same whether it's run from the project root or from
# inside src/, and when scheduled via cron with an absolute script path.
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _root_path(relative_path):
    override = os.getenv(relative_path.upper().replace("/", "_"))
    return override if override else os.path.join(_PROJECT_ROOT, relative_path)


# Core pipeline runs on sqlite3 (stdlib, zero dependencies) by default.
DB_PATH = os.getenv("DB_PATH", os.path.join(_PROJECT_ROOT, "data", "orders.db"))

# For production, point this at MySQL instead (used by the optional
# SQLAlchemy/FastAPI layer) — see README "Switching to MySQL".
DB_URL = os.getenv("DB_URL", f"sqlite:///{DB_PATH}")

# Slack webhook URL for alerts (optional). If not set, alerts are logged
# to console + logs/alerts.log instead of being sent anywhere.
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")

# Email alert settings (optional)
ALERT_EMAIL_TO = os.getenv("ALERT_EMAIL_TO", "")
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# Validation thresholds — tune these per dataset
NULL_RATE_THRESHOLD = 0.05        # flag a column if >5% of values are null
ROW_COUNT_DROP_THRESHOLD = 0.20   # flag if today's row count drops >20% vs yesterday
OUT_OF_RANGE_COLUMNS = {
    "amount": (0, 100000),        # (min, max) accepted range
    "quantity": (1, 500),
}

REPORTS_DIR = os.path.join(_PROJECT_ROOT, "reports")
LOGS_DIR = os.path.join(_PROJECT_ROOT, "logs")
