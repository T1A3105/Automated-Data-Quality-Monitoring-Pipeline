"""
Generates the daily data quality summary report in JSON and Markdown.
"""

import json
import os
from datetime import datetime

import config


def generate_report(day_label: str, row_count: int, issues: list):
    os.makedirs(config.REPORTS_DIR, exist_ok=True)

    critical = [i for i in issues if i["severity"] == "critical"]
    warning = [i for i in issues if i["severity"] == "warning"]

    report = {
        "generated_at": datetime.now().isoformat(),
        "day": day_label,
        "rows_checked": row_count,
        "status": "FAIL" if critical else ("WARN" if warning else "PASS"),
        "issue_count": len(issues),
        "critical_count": len(critical),
        "warning_count": len(warning),
        "issues": issues,
    }

    json_path = os.path.join(config.REPORTS_DIR, f"report_{day_label}.json")
    with open(json_path, "w") as f:
        json.dump(report, f, indent=2)

    md_path = os.path.join(config.REPORTS_DIR, f"report_{day_label}.md")
    with open(md_path, "w") as f:
        f.write(f"# Data Quality Report — {day_label}\n\n")
        f.write(f"**Generated:** {report['generated_at']}\n\n")
        f.write(f"**Status:** {report['status']}\n\n")
        f.write(f"**Rows checked:** {row_count}\n\n")
        f.write(f"**Issues found:** {len(issues)} "
                f"({len(critical)} critical, {len(warning)} warning)\n\n")
        if issues:
            f.write("| Severity | Check | Detail |\n|---|---|---|\n")
            for i in issues:
                f.write(f"| {i['severity']} | {i['check']} | {i['detail']} |\n")
        else:
            f.write("No data quality issues detected. ✅\n")

    # Always refresh a "latest" pointer for the API to read
    latest_path = os.path.join(config.REPORTS_DIR, "latest.json")
    with open(latest_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"[report] Wrote {json_path} and {md_path}")
    return report
