import csv
import json
import sqlite3
import tempfile
import unittest
from email import policy
from email.parser import BytesParser
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo
from player_report.pipeline import FIELDS, cents, load_snapshot, run, send_once
from player_report.generate_demo import generate


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "sessions.csv"

    def write(self, rows):
        with self.source.open("w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(FIELDS)
            writer.writerows(rows)

    def row(self, session, player, amount, stamp="2026-10-08T12:00:00-07:00"):
        return [session, player, "Demo North", stamp, amount]

    def report(self):
        return run(self.source, self.root / "out", self.root / "state.sqlite3", "2026-10-08")

    def test_strict_threshold_aggregation_and_duplicate_removal(self):
        a = self.row("S1", "P1", "6000.00")
        self.write([a, self.row("S2", "P1", "6000.00"), a,
                    self.row("S3", "P2", "10000.00"), self.row("S4", "P3", "10000.01")])
        summary = self.report()
        self.assertEqual(summary["qualified_players"], 2)
        self.assertEqual(summary["qualified_coin_in_cents"], 2200001)
        self.assertEqual(summary["duplicate_rows_removed"], 1)
        with (self.root / "out/high_coin_in_players_2026-10-08.csv").open(encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual([r["player_id"] for r in rows], ["P1", "P3"])
        self.assertEqual(rows[0]["session_count"], "2")

    def test_timezone_midnight_boundary(self):
        self.write([self.row("S1", "P1", "20000", "2026-10-09T06:59:59Z"),
                    self.row("S2", "P2", "20000", "2026-10-09T07:00:00Z")])
        self.assertEqual(self.report()["qualified_players"], 1)

    def test_invalid_rows_quarantined(self):
        self.write([self.row("S1", "P1", "10001"), self.row("S2", "P2", "-1"),
                    self.row("S3", "P3", "NaN"), self.row("S4", "P4", "1.234"),
                    self.row("S5", "=HYPERLINK", "11000"),
                    self.row("S6", "P6", "11000", "2026-10-08T12:00:00")])
        self.assertEqual(self.report()["rejected_rows"], 5)

    def test_conflicting_duplicate_preserves_previous_snapshot(self):
        self.write([self.row("S1", "P1", "12000")])
        connection = sqlite3.connect(":memory:")
        self.addCleanup(connection.close)
        load_snapshot(self.source, connection, ZoneInfo("America/Los_Angeles"))
        self.write([self.row("S2", "P2", "12000"), self.row("S2", "P2", "13000")])
        with self.assertRaisesRegex(ValueError, "conflicting duplicate"):
            load_snapshot(self.source, connection, ZoneInfo("America/Los_Angeles"))
        self.assertEqual(connection.execute("SELECT player_id FROM sessions").fetchone()[0], "P1")

    def test_repeat_load_does_not_double_count(self):
        generate(self.source)
        first, second = self.report(), self.report()
        self.assertEqual(first, second)
        self.assertEqual(first["email_status"], "draft_only")

    def test_email_draft_contains_csv_and_html_without_smtp(self):
        self.write([self.row("S1", "P1", "12000")])
        with patch("player_report.pipeline.smtplib.SMTP") as smtp:
            self.report()
            smtp.assert_not_called()
        msg = BytesParser(policy=policy.default).parsebytes((self.root / "out/email_preview_2026-10-08.eml").read_bytes())
        self.assertEqual(len(list(msg.iter_attachments())), 1)
        self.assertIn("P1", msg.get_body(preferencelist=("html",)).get_content())
        self.assertIn("12000.00", list(msg.iter_attachments())[0].get_payload(decode=True).decode("utf-8-sig"))

    def test_no_qualifiers_has_valid_header_only_report(self):
        self.write([self.row("S1", "P1", "10000")])
        self.assertEqual(self.report()["qualified_players"], 0)
        self.assertIn("No players exceeded", (self.root / "out/report_2026-10-08.html").read_text())

    def test_empty_or_stale_input_fails(self):
        self.write([])
        with self.assertRaisesRegex(ValueError, "no valid sessions"):
            self.report()
        self.write([self.row("S1", "P1", "12000", "2026-10-07T12:00:00-07:00")])
        with self.assertRaisesRegex(ValueError, "no valid sessions for"):
            self.report()

    def test_money_precision(self):
        self.assertEqual(cents("10000.01"), 1000001)
        for value in ["Inf", "NaN", "-1", "0.001", "abc"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                cents(value)

    def test_smtp_repeat_send_guard_and_failed_send_retry(self):
        connection = sqlite3.connect(":memory:")
        self.addCleanup(connection.close)
        environment = {"SMTP_HOST": "smtp.example.test", "SMTP_USER": "demo", "SMTP_PASSWORD": "fake",
                       "REPORT_FROM": "sender@example.test", "REPORT_TO": "recipient@example.test"}
        with patch("player_report.pipeline.smtplib.SMTP") as smtp:
            self.assertEqual(send_once(connection, "mock message", "day-key", environment), "sent")
            self.assertEqual(send_once(connection, "mock message", "day-key", environment), "already_sent")
            smtp.return_value.__enter__.return_value.send_message.assert_called_once()
        with patch("player_report.pipeline.smtplib.SMTP", side_effect=OSError("network failed")):
            with self.assertRaises(OSError):
                send_once(connection, "mock message", "new-key", environment)
        self.assertIsNone(connection.execute("SELECT 1 FROM sent_reports WHERE report_key='new-key'").fetchone())


if __name__ == "__main__":
    unittest.main()
