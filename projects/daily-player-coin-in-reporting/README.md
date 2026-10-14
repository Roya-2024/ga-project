# Daily Player Coin-In Reporting

A runnable data-engineering portfolio demo by Zahra Moradpour. It finds players whose **total daily Coin-In is strictly greater than $10,000**, creates an Excel-compatible CSV report and an HTML summary, and prepares an email with the report attached.

**All records are generated synthetic data.** This project is inspired by a reporting workflow; it does not use employer systems, real players, or confidential records. No email is sent by default.

## Business question

Which players exceeded the daily wagering-volume threshold, across all locations, yesterday? The output gives one row per qualifying player, their total Coin-In, session count, and locations. Coin-In means amount wagered; it is **not revenue, profit, or player losses**.

## Run the demo

Clone the portfolio repository and open this project folder:

```bash
git clone https://github.com/Roya-2024/ga-project.git
cd ga-project/projects/daily-player-coin-in-reporting
```

With Python 3.12+ (no pip dependencies):

```bash
python -m player_report --date 2026-10-08
python -m unittest discover -s tests -v
```

Windows: use `py -3.12` instead of `python` if needed. Windows Python may require the IANA timezone package: `py -3.12 -m pip install tzdata`. Linux/Docker uses system timezone data.

With Docker Desktop running:

```bash
docker compose build
docker compose run --rm report --date 2026-10-08
```

This is a **one-shot batch container**, so exiting after the report is complete is expected. No web server or exposed port is needed. On Linux, the bind-mounted `reports` directory must be writable by container UID 10001; create it and set ownership before running. Windows Docker Desktop typically manages bind-mount permissions.

Open `reports/report_2026-10-08.html` in a browser, the CSV in Excel, and `email_preview_2026-10-08.eml` in a mail application. Committed examples are in [sample_output](sample_output). SQLite state is stored in `state/` locally or in a Docker named volume.

## Verified sample result

For the included 2026-10-08 snapshot: 107 input rows, 1 exact duplicate removed, 1 invalid row quarantined, and 104 valid sessions on the report date. **19 players qualify, with $269,334.09 in combined Coin-In.** The previous-day session is excluded. These are synthetic demo results, not business performance claims.

## How it works

1. **Extract:** read a complete CSV extract of session-level data.
2. **Validate:** require identifiers, timestamp offsets, and non-negative amounts with cent precision. Quarantine invalid rows with row numbers and reasons. Remove exact duplicates; abort conflicting session IDs.
3. **Transform:** convert timestamps to `America/Los_Angeles`, store integer USD cents in SQLite, and aggregate per player with SQL `GROUP BY` and `HAVING`.
4. **Load/report:** export the qualifying list, quality results, HTML report, and JSON run summary.
5. **Distribute:** write an email draft by default. Explicit `--send` enables configured SMTP delivery.

See [the SQL query](sql/daily_high_coin_in.sql) and [business rules](docs/business_rules.md).

## Daily execution at 9:00 AM

The scheduler starts the job; Docker supplies its runtime. **A refreshed, complete input extract must arrive before each run.** The demo CSV is a fixed snapshot and cannot provide new real-world data automatically. A run without data for the requested day fails rather than producing a misleading empty report.

For a current-day synthetic practice file, run:

```bash
python -m player_report.generate_demo --date 2026-10-09
python -m player_report --date 2026-10-09
```

For Windows Task Scheduler:

- Create a daily 9:00 AM trigger in the computer's local timezone.
- Program: `powershell.exe`.
- Arguments: `-NoProfile -File "C:\FULL\PATH\daily-player-coin-in-reporting\scripts\run_daily.ps1"`.
- The script runs Docker once and defaults to the previous calendar day in Los Angeles.
- Docker Desktop and the machine must be running. Enable task history and inspect exit codes. For unattended reliability, deploy to an always-on host instead of relying on a sleeping laptop.

Linux cron example, on a host configured to the intended schedule timezone:

```cron
0 9 * * * cd /absolute/path/daily-player-coin-in-reporting && docker compose run --rm report --input data/demo_sessions.csv >> daily-report.log 2>&1
```

These are setup instructions; no scheduled task is installed or activated by this repository.

## Optional email delivery

Copy `.env.example` to `.env`, configure an approved SMTP account and recipient, and run:

```bash
docker compose run --rm report --date 2026-10-08 --send
```

STARTTLS and authentication are required. The configured sender/recipient are used to create the message. Default `.invalid` addresses cannot be used for delivery. Keep credentials outside GitHub. Local Python reads shell environment variables, not `.env`; Compose reads `.env` automatically.

A SQLite send ledger suppresses repeat sends for the same date, timezone, threshold, and recipient. Changed reports are not automatically resent under the same key; review corrections explicitly. SMTP acceptance followed by a process crash can still cause a duplicate on retry; this demo does not guarantee exactly-once email delivery. Do not run simultaneous deliveries with the same state database. Removing the state volume removes the send ledger.

## Tests and limitations

Automated tests cover the strict threshold, multiple-session aggregation, timezone cutoffs, duplicate handling, invalid records, repeated loads, stale inputs, email attachment contents, and the repeat-send guard. SMTP is mocked in tests. The Python pipeline has been run on the sample dataset; Docker configuration is provided for local execution.

This demo uses a complete snapshot, a calendar-day boundary, and session-start attribution. Production adapters, gaming-day cutoffs, currency conversion, corporate mail integration, access controls, monitoring, and verified source completeness must be defined for an actual deployment. Invalid rows are visibly excluded, so reports with rejections require review.

## Project files

| Path | Purpose |
|---|---|
| `player_report/pipeline.py` | ETL, SQL reporting, draft creation, optional SMTP |
| `player_report/generate_demo.py` | Reproducible synthetic-data generator |
| `data/demo_sessions.csv` | Fixed sample with boundary and quality cases |
| `sample_output/` | Actual output generated by this implementation |
| `tests/test_pipeline.py` | Business-rule and workflow tests |
| `Dockerfile`, `compose.yaml` | Container runtime and persistent state |
| `scripts/run_daily.ps1` | Scheduler entry point for Windows |

MIT licensed. Portfolio demo; no claim of deployment or measured employer impact.
