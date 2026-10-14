# Data contract and reporting rules

## Input

One row represents one session. A CSV input is a **complete snapshot** of all sessions required for the selected report date, optionally with surrounding dates. Each run replaces the current session snapshot atomically; it does not append incremental extracts.

| Field | Rule |
|---|---|
| `session_id` | Stable unique session identifier; alphanumeric start |
| `player_id` | Stable player identifier; no personal names required |
| `location` | Location label; no commas or formula characters |
| `session_start` | ISO 8601 timestamp with UTC offset, e.g. `2026-10-08T12:00:00-07:00` |
| `coin_in_usd` | Non-negative USD amount, at most two decimals, maximum $1 billion per session |

Identifier/label characters are limited to letters, digits, spaces, underscores, periods, and hyphens. This both normalizes the contract and prevents CSV formula injection. CSV headers must match the five fields exactly.

## Aggregation

- Report date: local calendar date of session start in `America/Los_Angeles`, configurable via `--timezone`.
- Default report date: yesterday in that timezone. A session crossing midnight is attributed entirely to its start date; no gaming-day or duration allocation is assumed.
- A player's sessions are aggregated across all locations.
- Threshold: **greater than** $10,000.00, not greater than or equal to. `--threshold` changes the rule.
- Integer cents are used for sums and comparisons; decimal currency text is used for CSV presentation.
- Results are sorted by Coin-In descending, then player ID ascending.

## Data quality

Exact duplicate sessions are discarded. Conflicting copies of the same session ID abort the load and preserve the previous snapshot. Invalid records are excluded with a reason and input row number in a quality report. A snapshot with no valid rows, or no valid rows on the report date, stops with a non-zero exit code. An otherwise valid report with zero qualifying players is still generated.

The synthetic input includes an exact $10,000 exclusion, a $10,000.01 inclusion, a duplicate, a negative amount, and a prior-day session. Coverage tests verify the rules independently.

## Persistence

Source CSV and reports are bind-mounted into Docker. SQLite and the email-send ledger live in a named volume. Recreating a container therefore preserves state; `docker compose down -v` deletes the named volume and its send history. Installed code is built into the image from a versioned Dockerfile; manual `docker exec` package installation is not required.

## Real deployment decisions

Before connecting a work system, confirm the metric, currency, gaming-day cutoff, cross-location scope, source completeness, and approved recipients with the business owner. This demo assumes USD and a calendar day. A real source connector and credentials are not included.
