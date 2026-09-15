"""
Sends alerts for detected data quality issues.

Alerts go to Slack (if SLACK_WEBHOOK_URL is set) and/or email (if SMTP
settings are set). If neither is configured, alerts are still logged to
logs/alerts.log and printed to console, so the pipeline is fully
functional and demoable with zero external accounts.
"""

import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText

import requests

import config


def _log_locally(message: str):
    os.makedirs(config.LOGS_DIR, exist_ok=True)
    path = os.path.join(config.LOGS_DIR, "alerts.log")
    with open(path, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {message}\n")


def _send_slack(message: str):
    if not config.SLACK_WEBHOOK_URL:
        return False
    try:
        resp = requests.post(config.SLACK_WEBHOOK_URL, json={"text": message}, timeout=5)
        return resp.status_code == 200
    except requests.RequestException as e:
        _log_locally(f"Slack send failed: {e}")
        return False


def _send_email(subject: str, body: str):
    if not (config.ALERT_EMAIL_TO and config.SMTP_HOST and config.SMTP_USER):
        return False
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = config.SMTP_USER
        msg["To"] = config.ALERT_EMAIL_TO
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
            server.starttls()
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        _log_locally(f"Email send failed: {e}")
        return False


def send_alerts(issues: list):
    """Sends one alert covering all issues found in a run. Always logs locally."""
    if not issues:
        message = "Data quality check passed — no issues found."
        _log_locally(message)
        print(f"[alerts] {message}")
        return

    critical = [i for i in issues if i["severity"] == "critical"]
    warning = [i for i in issues if i["severity"] == "warning"]

    lines = [f"Data Quality Alert — {len(issues)} issue(s) found "
             f"({len(critical)} critical, {len(warning)} warning)"]
    for issue in issues:
        lines.append(f"  [{issue['severity'].upper()}] {issue['check']}: {issue['detail']}")
    message = "\n".join(lines)

    _log_locally(message)
    print(f"[alerts]\n{message}")

    sent_slack = _send_slack(message)
    sent_email = _send_email("Data Quality Alert", message)

    if not sent_slack and not config.SLACK_WEBHOOK_URL:
        print("[alerts] (SLACK_WEBHOOK_URL not set — alert logged locally only)")
    if not sent_email and not config.ALERT_EMAIL_TO:
        print("[alerts] (ALERT_EMAIL_TO/SMTP not set — alert logged locally only)")
