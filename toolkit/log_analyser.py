"""Reusable parsing and filtering logic for plain-text technical logs."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from ipaddress import IPv4Address
import re
from typing import Iterable


SEVERITY_LEVELS = (
    "DEBUG",
    "INFO",
    "NOTICE",
    "WARNING",
    "ERROR",
    "CRITICAL",
    "UNCLASSIFIED",
)

SEVERITY_ALIASES = {
    "WARN": "WARNING",
    "FATAL": "CRITICAL",
}

TIMESTAMP_PATTERN = re.compile(
    r"\b\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}"
    r"(?:[.,]\d{1,6})?(?:Z|[+-]\d{2}:?\d{2})?\b"
)
SEVERITY_PATTERN = re.compile(
    r"\b(CRITICAL|WARNING|NOTICE|ERROR|DEBUG|INFO|FATAL|WARN)\b",
    re.IGNORECASE,
)
IPV4_CANDIDATE_PATTERN = re.compile(
    r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])"
)


class LogInputError(ValueError):
    """Raised when log content cannot be decoded or contains no entries."""


@dataclass(frozen=True)
class LogEntry:
    """One non-empty line extracted from a text log."""

    line_number: int
    timestamp: str | None
    severity: str
    ip_addresses: tuple[str, ...]
    raw_text: str


@dataclass(frozen=True)
class LogAnalysis:
    """Summary information and parsed entries for one text log."""

    total_lines: int
    non_empty_lines: int
    timestamped_entries: int
    severity_counts: dict[str, int]
    ip_counts: dict[str, int]
    entries: tuple[LogEntry, ...]

    @property
    def unique_ip_count(self) -> int:
        """Return the number of distinct valid IPv4 addresses found."""

        return len(self.ip_counts)


def decode_log_bytes(data: bytes) -> str:
    """Decode an uploaded text log as UTF-8, accepting an optional BOM."""

    if not isinstance(data, bytes):
        raise LogInputError("The uploaded log must be supplied as file bytes.")

    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise LogInputError(
            "The file could not be read as UTF-8 text. Convert it to UTF-8 and try again."
        ) from error


def extract_ipv4_addresses(line: str) -> tuple[str, ...]:
    """Return valid IPv4 addresses from a line while ignoring invalid candidates."""

    addresses: list[str] = []
    for candidate in IPV4_CANDIDATE_PATTERN.findall(line):
        try:
            address = IPv4Address(candidate)
        except ValueError:
            continue
        addresses.append(str(address))

    return tuple(addresses)


def _extract_severity(line: str) -> str:
    match = SEVERITY_PATTERN.search(line)
    if match is None:
        return "UNCLASSIFIED"

    severity = match.group(1).upper()
    return SEVERITY_ALIASES.get(severity, severity)


def _extract_timestamp(line: str) -> str | None:
    match = TIMESTAMP_PATTERN.search(line)
    return match.group(0) if match else None


def parse_log(text: str) -> LogAnalysis:
    """Parse non-empty entries and produce a deterministic log summary."""

    if not isinstance(text, str):
        raise LogInputError("Log content must be supplied as text.")

    lines = text.splitlines()
    severity_counts = Counter({level: 0 for level in SEVERITY_LEVELS})
    ip_counts: Counter[str] = Counter()
    entries: list[LogEntry] = []

    for line_number, raw_line in enumerate(lines, start=1):
        if not raw_line.strip():
            continue

        severity = _extract_severity(raw_line)
        timestamp = _extract_timestamp(raw_line)
        ip_addresses = extract_ipv4_addresses(raw_line)

        severity_counts[severity] += 1
        ip_counts.update(ip_addresses)
        entries.append(
            LogEntry(
                line_number=line_number,
                timestamp=timestamp,
                severity=severity,
                ip_addresses=ip_addresses,
                raw_text=raw_line.strip(),
            )
        )

    if not entries:
        raise LogInputError("The log does not contain any non-empty entries to analyse.")

    ordered_ip_counts = {
        address: ip_counts[address]
        for address in sorted(ip_counts, key=IPv4Address)
    }

    return LogAnalysis(
        total_lines=len(lines),
        non_empty_lines=len(entries),
        timestamped_entries=sum(entry.timestamp is not None for entry in entries),
        severity_counts=dict(severity_counts),
        ip_counts=ordered_ip_counts,
        entries=tuple(entries),
    )


def filter_entries(
    entries: Iterable[LogEntry],
    *,
    severity: str | None = None,
    ip_address: str | None = None,
    keyword: str | None = None,
) -> tuple[LogEntry, ...]:
    """Filter parsed entries using optional severity, IPv4 and keyword values."""

    normalised_severity = severity.upper().strip() if severity else None
    if normalised_severity and normalised_severity not in SEVERITY_LEVELS:
        raise LogInputError(f"Unknown severity filter: {severity}.")

    normalised_ip = ip_address.strip() if ip_address else None
    normalised_keyword = keyword.strip().casefold() if keyword else None

    filtered_entries = []
    for entry in entries:
        if normalised_severity and entry.severity != normalised_severity:
            continue
        if normalised_ip and normalised_ip not in entry.ip_addresses:
            continue
        if normalised_keyword and normalised_keyword not in entry.raw_text.casefold():
            continue
        filtered_entries.append(entry)

    return tuple(filtered_entries)
