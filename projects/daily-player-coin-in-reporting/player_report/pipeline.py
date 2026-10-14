"""Daily CSV -> validation -> SQLite/SQL -> report -> email draft pipeline.

Python standard library only. SMTP is opt-in; the default never sends email.
"""
import argparse
import csv
import hashlib
import html
import json
import logging
import os
import re
import smtplib
import sqlite3
import ssl
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from email.message import EmailMessage
from pathlib import Path
from zoneinfo import ZoneInfo

FIELDS = ["session_id", "player_id", "location", "session_start", "coin_in_usd"]
REPORT_FIELDS = ["report_date", "player_id", "locations", "session_count", "coin_in_usd"]
QUERY = """
SELECT player_id, GROUP_CONCAT(DISTINCT location) AS locations,
       COUNT(*) AS session_count, SUM(coin_in_cents) AS coin_in_cents
FROM sessions WHERE report_date = ?
GROUP BY player_id HAVING SUM(coin_in_cents) > ?
ORDER BY coin_in_cents DESC, player_id ASC
"""


def cents(value):
    """Reject negative, non-finite, fractional-cent or excessive money values."""
    try:
        amount = Decimal(str(value).strip())
        if not amount.is_finite() or amount < 0 or amount > Decimal("1000000000"):
            raise ValueError("amount must be finite and between 0 and 1,000,000,000")
        scaled = amount * 100
        if scaled != scaled.to_integral_value():
            raise ValueError("amount must have at most two decimal places")
        return int(scaled)
    except InvalidOperation as exc:
        raise ValueError("amount must be numeric") from exc


def normalize(row, tz):
    for field in FIELDS:
        if row.get(field) is None or not row[field].strip():
            raise ValueError(f"missing {field}")
    # Restrict identifiers to prevent formula execution when CSV is opened in Excel.
    for field in ["session_id", "player_id", "location"]:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 _.-]{0,79}", row[field].strip()):
            raise ValueError(f"invalid {field}")
    started = datetime.fromisoformat(row["session_start"].strip().replace("Z", "+00:00"))
    if started.tzinfo is None or started.utcoffset() is None:
        raise ValueError("session_start must include a UTC offset")
    return (row["session_id"].strip(), row["player_id"].strip(),
            row["location"].strip(), started.astimezone(timezone.utc).isoformat(),
            started.astimezone(tz).date().isoformat(), cents(row["coin_in_usd"]))


def load_snapshot(source, connection, tz):
    """Replace the current extract atomically; quarantine bad rows, deduplicate IDs.

    Conflicting duplicate IDs abort the whole load, preserving the previous snapshot.
    This is a complete-extract input contract, NOT incremental ingestion.
    """
    valid, rejected, duplicates = {}, [], 0
    with Path(source).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or set(reader.fieldnames) != set(FIELDS):
            raise ValueError(f"CSV headers must be exactly: {', '.join(FIELDS)}")
        for number, row in enumerate(reader, 2):
            try:
                if None in row:
                    raise ValueError("too many columns")
                item = normalize(row, tz)
            except (ValueError, TypeError, AttributeError) as exc:
                rejected.append({"row_number": number, "reason": str(exc)})
                continue
            if item[0] in valid:
                if valid[item[0]] != item:
                    raise ValueError(f"conflicting duplicate session_id: {item[0]}")
                duplicates += 1
            else:
                valid[item[0]] = item
    # Empty/entirely invalid extracts should not produce a misleading 'no players' report.
    if not valid:
        raise ValueError("no valid sessions; report withheld")
    connection.execute("""CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY, player_id TEXT NOT NULL, location TEXT NOT NULL,
        session_start_utc TEXT NOT NULL, report_date TEXT NOT NULL,
        coin_in_cents INTEGER NOT NULL CHECK(coin_in_cents >= 0))""")
    with connection:
        connection.execute("DELETE FROM sessions")
        connection.executemany("INSERT INTO sessions VALUES (?,?,?,?,?,?)", valid.values())
    return {"valid_sessions": len(valid), "duplicate_rows_removed": duplicates,
            "rejected_rows": len(rejected)}, rejected


def select_players(connection, report_date, threshold):
    return [{"report_date": report_date, "player_id": player,
             "locations": ", ".join(sorted(locations.split(","))),
             "session_count": count, "coin_in_usd": f"{Decimal(total)/100:.2f}"}
            for player, locations, count, total in connection.execute(QUERY, (report_date, threshold))]


def write_csv(path, fields, rows):
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def render_html(rows, summary):
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(row[key]))}</td>"
                   for key in REPORT_FIELDS) + "</tr>" for row in rows)
    if not body:
        body = '<tr><td colspan="5">No players exceeded the threshold.</td></tr>'
    return f"""<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Daily player Coin-In report</title><style>
body{{font:16px system-ui,sans-serif;background:#f1f5f9;color:#172337;margin:0;padding:32px}}
main{{max-width:1100px;margin:auto;background:white;padding:30px;border-radius:12px}}
h1{{margin:10px 0;color:#143859}} .label{{color:#536579;font-size:14px}}
.metrics{{display:flex;gap:32px;flex-wrap:wrap;background:#e9f3f6;padding:22px;margin:24px 0}}
.metrics strong{{display:block;font-size:28px;color:#125361}}
table{{border-collapse:collapse;width:100%;font-size:14px}}th,td{{text-align:left;padding:12px;border-bottom:1px solid #dce3ea}}
th{{background:#143859;color:white}} .table-wrap{{overflow:auto}}</style>
<main><p class="label">SYNTHETIC DATA · PORTFOLIO DEMO</p><h1>Daily player Coin-In report</h1>
<p>{summary['report_date']} · {html.escape(summary['timezone'])} · Daily total strictly greater than
${Decimal(summary['threshold_cents'])/100:,.2f}</p>
<div class="metrics"><div><strong>{summary['qualified_players']}</strong>Qualifying players</div>
<div><strong>${Decimal(summary['qualified_coin_in_cents'])/100:,.2f}</strong>Qualifying Coin-In</div>
<div><strong>{summary['report_date_sessions']}</strong>Valid sessions on report date</div></div>
<p>Quality review: {summary['duplicate_rows_removed']} duplicate rows removed;
{summary['rejected_rows']} invalid rows quarantined. Coin-In is wagering volume, not casino revenue.</p>
<div class="table-wrap"><table><thead><tr><th>Date</th><th>Player ID</th><th>Locations</th>
<th>Sessions</th><th>Coin-In (USD)</th></tr></thead><tbody>{body}</tbody></table></div>
<p class="label">Calendar-day aggregation across all locations. This demo has no real player records.</p></main></html>"""


def build_email(summary, report_html, csv_path, sender, recipient):
    msg = EmailMessage()
    msg["Subject"] = f"[DEMO] Daily Coin-In report — {summary['report_date']}"
    msg["From"], msg["To"] = sender, recipient
    msg.set_content(f"Synthetic-data demo for {summary['report_date']}.\n"
                    f"{summary['qualified_players']} players exceeded the daily threshold.\n"
                    f"{summary['rejected_rows']} invalid rows were excluded; review quality results.\n"
                    "The Excel-compatible CSV report is attached. Coin-In is not revenue.\n")
    msg.add_alternative(report_html, subtype="html")
    msg.add_attachment(csv_path.read_bytes(), maintype="text", subtype="csv", filename=csv_path.name)
    return msg


def send_once(connection, msg, key, environment=None):
    """Prevent ordinary repeat sends; SMTP cannot guarantee exactly-once delivery."""
    env = os.environ if environment is None else environment
    required = ["SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD", "REPORT_FROM", "REPORT_TO"]
    if any(not env.get(name) for name in required):
        raise ValueError("sending requires SMTP_HOST/USER/PASSWORD and REPORT_FROM/TO")
    if any(".invalid" in env[name] or "\n" in env[name] for name in ["REPORT_FROM", "REPORT_TO"]):
        raise ValueError("set real, approved sender and recipient addresses before sending")
    connection.execute("CREATE TABLE IF NOT EXISTS sent_reports (report_key TEXT PRIMARY KEY, sent_at TEXT)")
    if connection.execute("SELECT 1 FROM sent_reports WHERE report_key=?", (key,)).fetchone():
        return "already_sent"
    with smtplib.SMTP(env["SMTP_HOST"], int(env.get("SMTP_PORT", "587")), timeout=30) as smtp:
        smtp.starttls(context=ssl.create_default_context())
        smtp.login(env["SMTP_USER"], env["SMTP_PASSWORD"])
        smtp.send_message(msg)
    with connection:
        connection.execute("INSERT INTO sent_reports VALUES (?,?)", (key, datetime.now(timezone.utc).isoformat()))
    return "sent"


def run(source, output, database, report_date, timezone_name="America/Los_Angeles",
        threshold_usd="10000", send=False):
    tz, threshold = ZoneInfo(timezone_name), cents(threshold_usd)
    day = date.fromisoformat(report_date).isoformat()
    output, database = Path(output), Path(database)
    output.mkdir(parents=True, exist_ok=True)
    database.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database) as connection:
        quality, rejected = load_snapshot(source, connection, tz)
        sessions = connection.execute("SELECT COUNT(*) FROM sessions WHERE report_date=?", (day,)).fetchone()[0]
        if sessions == 0:
            raise ValueError(f"no valid sessions for {day}; report withheld (check input freshness/date)")
        rows = select_players(connection, day, threshold)
        summary = {"synthetic_demo": True, "report_date": day, "timezone": timezone_name,
                   "threshold_cents": threshold, "qualified_players": len(rows),
                   "qualified_coin_in_cents": sum(cents(r["coin_in_usd"]) for r in rows),
                   "report_date_sessions": sessions, **quality}
        csv_path = output / f"high_coin_in_players_{day}.csv"
        write_csv(csv_path, REPORT_FIELDS, rows)
        write_csv(output / f"rejected_rows_{day}.csv", ["row_number", "reason"], rejected)
        report_html = render_html(rows, summary)
        (output / f"report_{day}.html").write_text(report_html, encoding="utf-8")
        sender = os.getenv("REPORT_FROM", "report-demo@example.invalid")
        recipient = os.getenv("REPORT_TO", "manager-demo@example.invalid")
        msg = build_email(summary, report_html, csv_path, sender, recipient)
        (output / f"email_preview_{day}.eml").write_bytes(msg.as_bytes())
        key = hashlib.sha256(json.dumps([day, timezone_name, threshold, recipient], sort_keys=True).encode()).hexdigest()
        summary["email_status"] = send_once(connection, msg, key) if send else "draft_only"
        (output / f"summary_{day}.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="data/demo_sessions.csv")
    parser.add_argument("--output", default="reports")
    parser.add_argument("--database", default="state/reporting.sqlite3")
    parser.add_argument("--timezone", default="America/Los_Angeles")
    parser.add_argument("--date", help="YYYY-MM-DD; defaults to yesterday in the reporting timezone")
    parser.add_argument("--threshold", default="10000", help="strict daily Coin-In threshold in USD")
    parser.add_argument("--send", action="store_true", help="opt in to configured SMTP delivery")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        report_date = args.date or (datetime.now(ZoneInfo(args.timezone)).date() - timedelta(days=1)).isoformat()
        summary = run(args.input, args.output, args.database, report_date, args.timezone, args.threshold, args.send)
        logging.info(json.dumps(summary, sort_keys=True))
        return 0
    except (ValueError, OSError, sqlite3.Error, smtplib.SMTPException, KeyError) as exc:
        logging.error("report failed: %s", exc)
        return 1
