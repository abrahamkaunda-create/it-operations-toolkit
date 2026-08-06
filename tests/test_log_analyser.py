"""Unit tests for plain-text log parsing and filtering."""

import unittest

from toolkit.log_analyser import (
    LogInputError,
    decode_log_bytes,
    extract_ipv4_addresses,
    filter_entries,
    parse_log,
)


SAMPLE_LOG = """2026-08-06 08:00:01 INFO auth-service Login from 192.168.10.25
2026-08-06 08:01:12 WARN storage-service Disk usage reached 85 percent
2026-08-06 08:02:40 ERROR backup-service Connection to 10.20.0.15 failed
2026-08-06 08:03:02 FATAL network-service Gateway 10.0.0.1 unreachable
2026-08-06 08:04:19 DEBUG dns-service Query from 192.168.10.25 to 192.168.10.2
2026-08-06 08:05:00 healthcheck completed
"""


class ParseLogTests(unittest.TestCase):
    def test_summarises_severity_levels_and_aliases(self) -> None:
        analysis = parse_log(SAMPLE_LOG)

        self.assertEqual(analysis.non_empty_lines, 6)
        self.assertEqual(analysis.severity_counts["INFO"], 1)
        self.assertEqual(analysis.severity_counts["WARNING"], 1)
        self.assertEqual(analysis.severity_counts["ERROR"], 1)
        self.assertEqual(analysis.severity_counts["CRITICAL"], 1)
        self.assertEqual(analysis.severity_counts["DEBUG"], 1)
        self.assertEqual(analysis.severity_counts["UNCLASSIFIED"], 1)

    def test_extracts_timestamps_and_ipv4_addresses(self) -> None:
        analysis = parse_log(SAMPLE_LOG)

        self.assertEqual(analysis.timestamped_entries, 6)
        self.assertEqual(analysis.unique_ip_count, 4)
        self.assertEqual(analysis.ip_counts["192.168.10.25"], 2)
        self.assertEqual(analysis.entries[0].timestamp, "2026-08-06 08:00:01")

    def test_extracts_multiple_addresses_and_ignores_invalid_candidates(self) -> None:
        addresses = extract_ipv4_addresses(
            "Route changed from 10.0.0.1 to 10.0.0.254; ignored 999.10.10.10"
        )

        self.assertEqual(addresses, ("10.0.0.1", "10.0.0.254"))

    def test_filters_by_severity(self) -> None:
        analysis = parse_log(SAMPLE_LOG)

        entries = filter_entries(analysis.entries, severity="error")

        self.assertEqual(len(entries), 1)
        self.assertIn("backup-service", entries[0].raw_text)

    def test_filters_by_ip_address(self) -> None:
        analysis = parse_log(SAMPLE_LOG)

        entries = filter_entries(analysis.entries, ip_address="192.168.10.25")

        self.assertEqual(len(entries), 2)

    def test_filters_by_case_insensitive_keyword(self) -> None:
        analysis = parse_log(SAMPLE_LOG)

        entries = filter_entries(analysis.entries, keyword="GATEWAY")

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].severity, "CRITICAL")

    def test_combines_filters(self) -> None:
        analysis = parse_log(SAMPLE_LOG)

        entries = filter_entries(
            analysis.entries,
            severity="DEBUG",
            ip_address="192.168.10.2",
            keyword="query",
        )

        self.assertEqual(len(entries), 1)

    def test_rejects_unknown_severity_filter(self) -> None:
        analysis = parse_log(SAMPLE_LOG)

        with self.assertRaises(LogInputError):
            filter_entries(analysis.entries, severity="EMERGENCY")

    def test_rejects_empty_log_content(self) -> None:
        for value in ("", "  \n\t\n"):
            with self.subTest(value=value):
                with self.assertRaises(LogInputError):
                    parse_log(value)

    def test_decodes_utf8_bytes_with_optional_bom(self) -> None:
        decoded = decode_log_bytes(b"\xef\xbb\xbf2026-08-06 08:00:01 INFO ready")

        self.assertEqual(decoded, "2026-08-06 08:00:01 INFO ready")

    def test_rejects_non_utf8_file_content(self) -> None:
        with self.assertRaises(LogInputError):
            decode_log_bytes(b"\xff\xfe\x00\x00")


if __name__ == "__main__":
    unittest.main()
